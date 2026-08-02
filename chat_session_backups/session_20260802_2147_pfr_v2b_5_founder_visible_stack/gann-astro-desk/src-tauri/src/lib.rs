use serde::Serialize;
use tauri::Manager;

#[cfg_attr(all(test, not(mobile)), allow(dead_code))]
#[cfg(any(mobile, test))]
mod companion_client;
#[cfg(not(mobile))]
mod companion_gateway;
mod companion_protocol;
#[cfg(not(mobile))]
use serde_json::{json, Value};
#[cfg(not(mobile))]
use std::collections::VecDeque;
#[cfg(not(mobile))]
use std::env;
#[cfg(not(mobile))]
use std::fs::{self, OpenOptions};
#[cfg(not(mobile))]
use std::io::{Read, Write};
#[cfg(not(mobile))]
use std::net::{IpAddr, Ipv4Addr, SocketAddr, TcpListener, TcpStream};
#[cfg(not(mobile))]
use std::path::{Path, PathBuf};
#[cfg(not(mobile))]
use std::process::{Child, Command, Stdio};
#[cfg(not(mobile))]
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Mutex,
};
#[cfg(not(mobile))]
use std::thread;
#[cfg(not(mobile))]
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
#[cfg(not(mobile))]
use tauri::{AppHandle, RunEvent, State};
#[cfg(not(mobile))]
use uuid::Uuid;

#[cfg(not(mobile))]
const SIDECAR_CONTRACT: &str = "GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1";
const RUNTIME_PROFILE_CONTRACT: &str = "GANN_ASTRO_RUNTIME_PROFILE_V1";
#[cfg(not(mobile))]
const MAX_RESTARTS: usize = 3;
#[cfg(not(mobile))]
const RESTART_WINDOW: Duration = Duration::from_secs(5 * 60);
#[cfg(not(mobile))]
const MAX_LOG_BYTES: u64 = 10 * 1024 * 1024;
#[cfg(not(mobile))]
const LOG_BACKUP_COUNT: usize = 3;

#[cfg(not(mobile))]
#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct BackendRuntimeInfo {
    contract: &'static str,
    base_url: String,
    api_token: String,
    port: u16,
    pid: u32,
    status: String,
    execution_allowed: bool,
    restart_count: u32,
    recovery_state: String,
    started_at_unix_ms: u64,
    spawn_elapsed_ms: u64,
    last_exit: Option<String>,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct RuntimeProfile {
    contract: &'static str,
    platform: &'static str,
    backend_mode: &'static str,
    configured: bool,
    execution_allowed: bool,
}

#[cfg(not(mobile))]
#[derive(Clone)]
enum SidecarLaunch {
    Executable(PathBuf),
    SourcePython { python: PathBuf, script: PathBuf },
}

#[cfg(not(mobile))]
struct ManagedChild {
    process: Child,
    #[cfg(windows)]
    _job: std::os::windows::io::OwnedHandle,
}

#[cfg(not(mobile))]
impl ManagedChild {
    fn new(process: Child) -> Result<Self, String> {
        #[cfg(windows)]
        {
            let job = assign_kill_on_close_job(&process)?;
            Ok(Self { process, _job: job })
        }
        #[cfg(not(windows))]
        {
            Ok(Self { process })
        }
    }

    fn id(&self) -> u32 {
        self.process.id()
    }
}

#[cfg(not(mobile))]
struct SupervisorProcess {
    child: Option<ManagedChild>,
    restart_times: VecDeque<Instant>,
    restart_count: u32,
    started_at_unix_ms: u64,
    spawn_elapsed_ms: u64,
    last_exit: Option<String>,
}

#[cfg(not(mobile))]
struct BackendRuntimeState {
    base_url: String,
    api_token: String,
    port: u16,
    codex_port: u16,
    launch: SidecarLaunch,
    data_root: PathBuf,
    logs_dir: PathBuf,
    process: Mutex<SupervisorProcess>,
    shutting_down: AtomicBool,
}

#[cfg(not(mobile))]
fn now_unix_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
        .try_into()
        .unwrap_or(u64::MAX)
}

#[cfg(not(mobile))]
fn validated_api_token_override(value: &str) -> Option<String> {
    let token = value.trim();
    if !(24..=128).contains(&token.len())
        || !token
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return None;
    }
    Some(token.to_string())
}

#[cfg(not(mobile))]
fn launch_api_token() -> String {
    env::var("GANN_ASTRO_API_TOKEN_OVERRIDE")
        .ok()
        .and_then(|value| validated_api_token_override(&value))
        .unwrap_or_else(|| Uuid::new_v4().simple().to_string())
}

#[cfg(not(mobile))]
fn available_port() -> Result<u16, String> {
    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0))
        .map_err(|error| format!("Unable to reserve a private backend port: {error}"))?;
    listener
        .local_addr()
        .map(|address| address.port())
        .map_err(|error| format!("Unable to read the private backend port: {error}"))
}

#[cfg(not(mobile))]
fn backup_log_path(path: &Path, index: usize) -> PathBuf {
    let name = path
        .file_name()
        .and_then(|value| value.to_str())
        .unwrap_or("runtime.log");
    path.with_file_name(format!("{name}.{index}"))
}

#[cfg(not(mobile))]
fn rotate_log_if_needed(path: &Path) -> Result<(), String> {
    let size = match fs::metadata(path) {
        Ok(metadata) => metadata.len(),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
        Err(error) => {
            return Err(format!(
                "Unable to inspect runtime log {}: {error}",
                path.display()
            ));
        }
    };
    if size < MAX_LOG_BYTES {
        return Ok(());
    }
    let oldest = backup_log_path(path, LOG_BACKUP_COUNT);
    if oldest.exists() {
        fs::remove_file(&oldest).map_err(|error| {
            format!(
                "Unable to remove old runtime log {}: {error}",
                oldest.display()
            )
        })?;
    }
    for index in (1..LOG_BACKUP_COUNT).rev() {
        let source = backup_log_path(path, index);
        if source.exists() {
            let destination = backup_log_path(path, index + 1);
            fs::rename(&source, &destination).map_err(|error| {
                format!(
                    "Unable to rotate runtime log {} to {}: {error}",
                    source.display(),
                    destination.display()
                )
            })?;
        }
    }
    let first_backup = backup_log_path(path, 1);
    fs::rename(path, &first_backup).map_err(|error| {
        format!(
            "Unable to rotate runtime log {} to {}: {error}",
            path.display(),
            first_backup.display()
        )
    })
}

#[cfg(not(mobile))]
fn parse_http_json_response(raw: &[u8]) -> Result<Value, String> {
    let split = raw
        .windows(4)
        .position(|window| window == b"\r\n\r\n")
        .ok_or_else(|| "Private sidecar returned an invalid HTTP response".to_string())?;
    let headers = std::str::from_utf8(&raw[..split])
        .map_err(|error| format!("Private sidecar returned invalid HTTP headers: {error}"))?;
    let mut lines = headers.lines();
    let status_line = lines
        .next()
        .ok_or_else(|| "Private sidecar response has no status line".to_string())?;
    let status = status_line
        .split_whitespace()
        .nth(1)
        .and_then(|value| value.parse::<u16>().ok())
        .ok_or_else(|| "Private sidecar response has an invalid status".to_string())?;
    if lines.any(|line| {
        line.to_ascii_lowercase()
            .starts_with("transfer-encoding: chunked")
    }) {
        return Err("Private sidecar used unsupported chunked encoding".to_string());
    }
    let payload = serde_json::from_slice::<Value>(&raw[split + 4..])
        .map_err(|error| format!("Private sidecar returned invalid JSON: {error}"))?;
    if !(200..300).contains(&status) {
        let detail = payload
            .get("error")
            .and_then(Value::as_str)
            .unwrap_or("Chakra Lab request failed");
        return Err(format!("Private sidecar returned HTTP {status}: {detail}"));
    }
    Ok(payload)
}

#[cfg(not(mobile))]
fn post_private_json(
    port: u16,
    api_token: &str,
    path: &str,
    payload: &Value,
) -> Result<Value, String> {
    if !path.starts_with('/') || path.contains(char::is_whitespace) {
        return Err("Private sidecar path is invalid".to_string());
    }
    let address = SocketAddr::new(IpAddr::V4(Ipv4Addr::LOCALHOST), port);
    let mut stream = TcpStream::connect_timeout(&address, Duration::from_secs(3))
        .map_err(|error| format!("Unable to connect to private sidecar: {error}"))?;
    stream
        .set_read_timeout(Some(Duration::from_secs(20)))
        .map_err(|error| format!("Unable to set sidecar read timeout: {error}"))?;
    stream
        .set_write_timeout(Some(Duration::from_secs(5)))
        .map_err(|error| format!("Unable to set sidecar write timeout: {error}"))?;
    let body = serde_json::to_vec(payload)
        .map_err(|error| format!("Unable to encode Chakra Lab request: {error}"))?;
    let request = format!(
        "POST {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\nAccept: application/json\r\nX-Gann-Astro-Token: {api_token}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
        body.len()
    );
    stream
        .write_all(request.as_bytes())
        .and_then(|_| stream.write_all(&body))
        .and_then(|_| stream.flush())
        .map_err(|error| format!("Unable to send Chakra Lab request: {error}"))?;
    let mut response = Vec::new();
    stream
        .read_to_end(&mut response)
        .map_err(|error| format!("Unable to read Chakra Lab response: {error}"))?;
    parse_http_json_response(&response)
}

#[cfg(not(mobile))]
fn default_data_root() -> PathBuf {
    if let Some(configured) = env::var_os("GANN_ASTRO_DESKTOP_DATA") {
        return PathBuf::from(configured);
    }
    if Path::new("D:\\").exists() {
        return PathBuf::from(r"D:\GannFinancialAstro\app_data");
    }
    env::var_os("LOCALAPPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(env::temp_dir)
        .join("GannAstroDesk")
}

#[cfg(not(mobile))]
fn locate_sidecar(app: &AppHandle) -> Result<SidecarLaunch, String> {
    if let Some(configured) = env::var_os("GANN_ASTRO_SIDECAR_EXE") {
        let executable = PathBuf::from(configured);
        if executable.is_file() {
            return Ok(SidecarLaunch::Executable(executable));
        }
        return Err(format!(
            "Configured backend sidecar does not exist: {}",
            executable.display()
        ));
    }

    let resource_executable = app
        .path()
        .resource_dir()
        .map_err(|error| format!("Unable to resolve application resources: {error}"))?
        .join("backend")
        .join("GannAstroBackend.exe");
    if resource_executable.is_file() {
        return Ok(SidecarLaunch::Executable(resource_executable));
    }

    if cfg!(debug_assertions) {
        let script = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .ok_or_else(|| "Unable to resolve the source application directory".to_string())?
            .join("backend_sidecar.py");
        if script.is_file() {
            let python = env::var_os("GANN_ASTRO_PYTHON")
                .map(PathBuf::from)
                .unwrap_or_else(|| PathBuf::from("python.exe"));
            return Ok(SidecarLaunch::SourcePython { python, script });
        }
    }

    Err(format!(
        "Managed backend sidecar is missing: {}",
        resource_executable.display()
    ))
}

#[cfg(not(mobile))]
fn configure_hidden_process(command: &mut Command) {
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        command.creation_flags(CREATE_NO_WINDOW);
    }
}

#[cfg(windows)]
fn assign_kill_on_close_job(child: &Child) -> Result<std::os::windows::io::OwnedHandle, String> {
    use std::mem::{size_of, zeroed};
    use std::os::windows::io::{AsRawHandle, FromRawHandle, OwnedHandle};
    use windows_sys::Win32::Foundation::GetLastError;
    use windows_sys::Win32::System::JobObjects::{
        AssignProcessToJobObject, CreateJobObjectW, JobObjectExtendedLimitInformation,
        SetInformationJobObject, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
    };

    unsafe {
        let raw_job = CreateJobObjectW(std::ptr::null(), std::ptr::null());
        if raw_job.is_null() {
            return Err(format!(
                "Unable to create sidecar job object: {}",
                GetLastError()
            ));
        }
        let job = OwnedHandle::from_raw_handle(raw_job.cast());
        let mut limits: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = zeroed();
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        if SetInformationJobObject(
            raw_job,
            JobObjectExtendedLimitInformation,
            (&limits as *const JOBOBJECT_EXTENDED_LIMIT_INFORMATION).cast(),
            size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
        ) == 0
        {
            return Err(format!(
                "Unable to configure sidecar job object: {}",
                GetLastError()
            ));
        }
        if AssignProcessToJobObject(raw_job, child.as_raw_handle().cast()) == 0 {
            return Err(format!(
                "Unable to attach sidecar to job object: {}",
                GetLastError()
            ));
        }
        Ok(job)
    }
}

#[cfg(not(mobile))]
fn spawn_sidecar(
    launch: &SidecarLaunch,
    data_root: &Path,
    logs_dir: &Path,
    port: u16,
    codex_port: u16,
    api_token: &str,
) -> Result<(ManagedChild, u64, u64), String> {
    let stdout_path = logs_dir.join("tauri_backend_sidecar.log");
    let stderr_path = logs_dir.join("tauri_backend_sidecar_error.log");
    rotate_log_if_needed(&stdout_path)?;
    rotate_log_if_needed(&stderr_path)?;
    rotate_log_if_needed(&logs_dir.join("tauri_runtime_supervisor.jsonl"))?;
    let stdout = OpenOptions::new()
        .create(true)
        .append(true)
        .open(stdout_path)
        .map_err(|error| format!("Unable to open backend sidecar log: {error}"))?;
    let stderr = OpenOptions::new()
        .create(true)
        .append(true)
        .open(stderr_path)
        .map_err(|error| format!("Unable to open backend sidecar error log: {error}"))?;

    let mut command = match launch {
        SidecarLaunch::Executable(executable) => {
            let mut command = Command::new(executable);
            if let Some(parent) = executable.parent() {
                command.current_dir(parent);
            }
            command
        }
        SidecarLaunch::SourcePython { python, script } => {
            let mut command = Command::new(python);
            command.arg(script);
            if let Some(parent) = script.parent() {
                command.current_dir(parent);
            }
            command
        }
    };
    command
        .arg("--port")
        .arg(port.to_string())
        .arg("--codex-port")
        .arg(codex_port.to_string())
        .env("GANN_ASTRO_DESKTOP_DATA", data_root)
        .env("GANN_ASTRO_API_TOKEN", api_token)
        .env("PYTHONUNBUFFERED", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::from(stdout))
        .stderr(Stdio::from(stderr));
    configure_hidden_process(&mut command);
    let spawn_started_at = Instant::now();
    let process = command
        .spawn()
        .map_err(|error| format!("Unable to start managed backend sidecar: {error}"))?;
    let managed = ManagedChild::new(process)?;
    let spawn_elapsed_ms = spawn_started_at
        .elapsed()
        .as_millis()
        .try_into()
        .unwrap_or(u64::MAX);
    Ok((managed, now_unix_ms(), spawn_elapsed_ms))
}

#[cfg(not(mobile))]
fn prune_restart_times(restart_times: &mut VecDeque<Instant>, now: Instant) {
    while restart_times
        .front()
        .is_some_and(|started| now.duration_since(*started) > RESTART_WINDOW)
    {
        restart_times.pop_front();
    }
}

#[cfg(not(mobile))]
impl BackendRuntimeState {
    fn spawn(app: &AppHandle) -> Result<Self, String> {
        let port = available_port()?;
        let codex_port = available_port()?;
        let api_token = launch_api_token();
        let launch = locate_sidecar(app)?;
        let data_root = default_data_root();
        let logs_dir = data_root.join("logs");
        fs::create_dir_all(&logs_dir)
            .map_err(|error| format!("Unable to create runtime logs: {error}"))?;
        let (child, started_at_unix_ms, spawn_elapsed_ms) =
            spawn_sidecar(&launch, &data_root, &logs_dir, port, codex_port, &api_token)?;
        let state = Self {
            base_url: format!("http://127.0.0.1:{port}"),
            api_token,
            port,
            codex_port,
            launch,
            data_root,
            logs_dir,
            process: Mutex::new(SupervisorProcess {
                child: Some(child),
                restart_times: VecDeque::new(),
                restart_count: 0,
                started_at_unix_ms,
                spawn_elapsed_ms,
                last_exit: None,
            }),
            shutting_down: AtomicBool::new(false),
        };
        state.append_supervisor_event("sidecar_spawned", None);
        Ok(state)
    }

    fn append_supervisor_event(&self, name: &str, details: Option<serde_json::Value>) {
        let event = json!({
            "atUnixMs": now_unix_ms(),
            "kind": "tauri_supervisor",
            "name": name,
            "details": details.unwrap_or_else(|| json!({})),
            "executionAllowed": false,
        });
        if let Ok(mut handle) = OpenOptions::new()
            .create(true)
            .append(true)
            .open(self.logs_dir.join("tauri_runtime_supervisor.jsonl"))
        {
            let _ = writeln!(handle, "{event}");
        }
    }

    fn restart_locked(&self, process: &mut SupervisorProcess) -> Result<(), String> {
        if self.shutting_down.load(Ordering::SeqCst) {
            return Err("Backend sidecar is shutting down".to_string());
        }
        let now = Instant::now();
        prune_restart_times(&mut process.restart_times, now);
        if process.restart_times.len() >= MAX_RESTARTS {
            self.append_supervisor_event(
                "restart_limit_reached",
                Some(json!({"restartCount": process.restart_count})),
            );
            return Err(format!(
                "Backend sidecar restart limit reached ({MAX_RESTARTS} attempts in five minutes)"
            ));
        }
        thread::sleep(Duration::from_millis(250));
        let (child, started_at_unix_ms, spawn_elapsed_ms) = spawn_sidecar(
            &self.launch,
            &self.data_root,
            &self.logs_dir,
            self.port,
            self.codex_port,
            &self.api_token,
        )?;
        process.child = Some(child);
        process.restart_times.push_back(now);
        process.restart_count += 1;
        process.started_at_unix_ms = started_at_unix_ms;
        process.spawn_elapsed_ms = spawn_elapsed_ms;
        self.append_supervisor_event(
            "sidecar_restarted",
            Some(json!({
                "restartCount": process.restart_count,
                "lastExit": process.last_exit,
            })),
        );
        Ok(())
    }

    fn snapshot(&self) -> Result<BackendRuntimeInfo, String> {
        let mut process = self
            .process
            .lock()
            .map_err(|_| "Backend sidecar state is unavailable".to_string())?;
        if let Some(child) = process.child.as_mut() {
            if let Some(status) = child
                .process
                .try_wait()
                .map_err(|error| format!("Unable to inspect backend sidecar: {error}"))?
            {
                let exit = status.to_string();
                process.last_exit = Some(exit.clone());
                process.child = None;
                self.append_supervisor_event(
                    "sidecar_exit_detected",
                    Some(json!({"status": exit})),
                );
            }
        }
        if process.child.is_none() {
            self.restart_locked(&mut process)?;
        }
        let child = process
            .child
            .as_ref()
            .ok_or_else(|| "Backend sidecar recovery did not start a process".to_string())?;
        let address = SocketAddr::new(IpAddr::V4(Ipv4Addr::LOCALHOST), self.port);
        let ready = TcpStream::connect_timeout(&address, Duration::from_millis(120)).is_ok();
        let recovery_state = if process.restart_count == 0 {
            "steady"
        } else if ready {
            "recovered"
        } else {
            "recovering"
        };
        Ok(BackendRuntimeInfo {
            contract: SIDECAR_CONTRACT,
            base_url: self.base_url.clone(),
            api_token: self.api_token.clone(),
            port: self.port,
            pid: child.id(),
            status: if ready { "ready" } else { "starting" }.to_string(),
            execution_allowed: false,
            restart_count: process.restart_count,
            recovery_state: recovery_state.to_string(),
            started_at_unix_ms: process.started_at_unix_ms,
            spawn_elapsed_ms: process.spawn_elapsed_ms,
            last_exit: process.last_exit.clone(),
        })
    }

    fn shutdown(&self) {
        self.shutting_down.store(true, Ordering::SeqCst);
        let Ok(mut process) = self.process.lock() else {
            return;
        };
        let Some(mut child) = process.child.take() else {
            return;
        };
        self.append_supervisor_event("sidecar_shutdown_requested", None);
        if let Some(stdin) = child.process.stdin.as_mut() {
            let _ = stdin.write_all(b"shutdown\n");
            let _ = stdin.flush();
        }
        let deadline = Instant::now() + Duration::from_secs(8);
        while Instant::now() < deadline {
            match child.process.try_wait() {
                Ok(Some(_)) => return,
                Ok(None) => thread::sleep(Duration::from_millis(100)),
                Err(_) => break,
            }
        }
        let _ = child.process.kill();
        let _ = child.process.wait();
    }
}

#[tauri::command]
fn runtime_profile() -> RuntimeProfile {
    #[cfg(mobile)]
    {
        RuntimeProfile {
            contract: RUNTIME_PROFILE_CONTRACT,
            platform: if cfg!(target_os = "android") {
                "android"
            } else {
                "mobile"
            },
            backend_mode: "remote_companion",
            configured: false,
            execution_allowed: false,
        }
    }
    #[cfg(not(mobile))]
    {
        RuntimeProfile {
            contract: RUNTIME_PROFILE_CONTRACT,
            platform: "desktop",
            backend_mode: "managed_sidecar",
            configured: true,
            execution_allowed: false,
        }
    }
}

#[cfg(not(mobile))]
#[tauri::command]
fn companion_gateway_info(
    state: State<'_, companion_gateway::CompanionGatewayState>,
) -> companion_gateway::GatewayInfo {
    state.info()
}

#[cfg(not(mobile))]
#[tauri::command]
fn companion_start_pairing(
    state: State<'_, companion_gateway::CompanionGatewayState>,
) -> Result<companion_gateway::PairingWindowInfo, String> {
    state.start_pairing()
}

#[cfg(not(mobile))]
#[tauri::command]
fn companion_gateway_sessions(
    state: State<'_, companion_gateway::CompanionGatewayState>,
) -> Vec<companion_gateway::GatewaySessionInfo> {
    state.sessions()
}

#[cfg(not(mobile))]
#[tauri::command]
fn companion_revoke_session(
    session_id: String,
    state: State<'_, companion_gateway::CompanionGatewayState>,
) -> bool {
    state.revoke(&session_id)
}

#[cfg(not(mobile))]
#[tauri::command]
fn backend_runtime(state: State<'_, BackendRuntimeState>) -> Result<BackendRuntimeInfo, String> {
    state.snapshot()
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_snapshot(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Chakra Lab requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/snapshot",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_audit(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Chakra Lab audit requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/audit",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab audit bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_fixed_phasor(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Chakra Lab fixed phasor requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/fixed-phasor",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab fixed phasor bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn synchronized_independent_range(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Synchronized fields require the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/independent-fields/synchronized-range",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Synchronized field bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_timing_profile_admission(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Timing profile admission requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/timing-profile/admission",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Timing profile admission bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_timing_source_packet_readiness(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err(
            "Timing source packet readiness requires the read-only runtime lock".to_string(),
        );
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/timing-profile/source-packet/readiness",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Timing source packet readiness bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_timing_source_verification(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Timing source verification requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/timing-profile/source-packet/verify-bytes",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Timing source verification bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_timing_external_review(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Timing external review requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/timing-profile/external-review/verify",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Timing external review bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_timing_signed_review(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Timing signed review requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/timing-profile/signed-review/verify",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Timing signed review bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_timing_source_certification(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Timing source certification requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/timing-profile/source-certification/verify",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Timing source certification bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_audit_package(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Chakra Lab audit package requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/audit-package",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab audit package bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_verify_audit_package(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err(
            "Chakra Lab audit package verification requires the read-only runtime lock".to_string(),
        );
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/audit-package/verify",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab package verification bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_audit_catalog(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err("Chakra Lab audit catalog requires the read-only runtime lock".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/audit-catalog",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab audit catalog bridge task failed: {error}"))?
}

#[cfg(not(mobile))]
#[tauri::command]
async fn chakra_lab_verify_audit_catalog(
    request: Value,
    state: State<'_, BackendRuntimeState>,
) -> Result<Value, String> {
    let runtime = state.snapshot()?;
    if runtime.execution_allowed {
        return Err(
            "Chakra Lab audit catalog verification requires the read-only runtime lock".to_string(),
        );
    }
    tauri::async_runtime::spawn_blocking(move || {
        post_private_json(
            runtime.port,
            &runtime.api_token,
            "/api/chakra-lab/audit-catalog/verify",
            &request,
        )
    })
    .await
    .map_err(|error| format!("Chakra Lab catalog verification bridge task failed: {error}"))?
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    companion_protocol::install_crypto_provider()
        .expect("Gann Astro could not initialize its TLS crypto provider");

    #[cfg(not(mobile))]
    let app = tauri::Builder::default()
        .setup(|app| {
            let backend = BackendRuntimeState::spawn(app.handle())?;
            let gateway = companion_gateway::CompanionGatewayState::spawn(
                backend.port,
                backend.api_token.clone(),
                backend.data_root.clone(),
            )?;
            app.manage(backend);
            app.manage(gateway);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            runtime_profile,
            backend_runtime,
            chakra_lab_snapshot,
            chakra_lab_audit,
            chakra_lab_fixed_phasor,
            synchronized_independent_range,
            chakra_lab_timing_profile_admission,
            chakra_lab_timing_source_packet_readiness,
            chakra_lab_timing_source_verification,
            chakra_lab_timing_external_review,
            chakra_lab_timing_signed_review,
            chakra_lab_timing_source_certification,
            chakra_lab_audit_package,
            chakra_lab_verify_audit_package,
            chakra_lab_audit_catalog,
            chakra_lab_verify_audit_catalog,
            companion_gateway_info,
            companion_start_pairing,
            companion_gateway_sessions,
            companion_revoke_session
        ])
        .build(tauri::generate_context!())
        .expect("Gann Astro Desk failed to build");

    #[cfg(mobile)]
    let app = tauri::Builder::default()
        .setup(|app| {
            app.manage(companion_client::MobileCompanionState::default());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            runtime_profile,
            companion_client::companion_pair,
            companion_client::companion_request,
            companion_client::companion_session,
            companion_client::companion_disconnect,
            companion_client::companion_start_stream
        ])
        .build(tauri::generate_context!())
        .expect("Gann Astro Mobile failed to build");

    #[cfg(not(mobile))]
    app.run(|app_handle, event| match event {
        RunEvent::Resumed => {
            let state = app_handle.state::<BackendRuntimeState>();
            let _ = state.snapshot();
        }
        RunEvent::ExitRequested { .. } | RunEvent::Exit => {
            app_handle
                .state::<companion_gateway::CompanionGatewayState>()
                .shutdown();
            app_handle.state::<BackendRuntimeState>().shutdown();
        }
        _ => {}
    });

    #[cfg(mobile)]
    app.run(|_, _| {});
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn restart_window_prunes_old_attempts() {
        let now = Instant::now();
        let mut attempts = VecDeque::from([
            now - RESTART_WINDOW - Duration::from_secs(1),
            now - Duration::from_secs(3),
        ]);
        prune_restart_times(&mut attempts, now);
        assert_eq!(attempts.len(), 1);
    }

    #[test]
    fn private_json_parser_accepts_success_and_surfaces_sidecar_errors() {
        let success = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 22\r\n\r\n{\"ok\":true,\"value\":7}";
        assert_eq!(
            parse_http_json_response(success).unwrap()["value"],
            json!(7)
        );

        let failure = b"HTTP/1.1 400 BAD REQUEST\r\nContent-Type: application/json\r\nContent-Length: 32\r\n\r\n{\"ok\":false,\"error\":\"bad time\"}";
        let error = parse_http_json_response(failure).unwrap_err();
        assert!(error.contains("HTTP 400"));
        assert!(error.contains("bad time"));
    }

    #[test]
    fn api_token_override_accepts_only_header_safe_values() {
        let valid = "0123456789abcdef0123456789abcdef";
        assert_eq!(validated_api_token_override(valid), Some(valid.to_string()));
        assert_eq!(validated_api_token_override("short"), None);
        assert_eq!(
            validated_api_token_override("0123456789abcdef01234567\r\nInjected: yes"),
            None
        );
    }

    #[test]
    fn oversized_runtime_logs_are_rotated_with_bounded_backups() {
        let root = env::temp_dir().join(format!(
            "gann-astro-log-rotation-{}-{}",
            std::process::id(),
            now_unix_ms()
        ));
        fs::create_dir_all(&root).unwrap();
        let path = root.join("runtime.log");
        let handle = fs::File::create(&path).unwrap();
        handle.set_len(MAX_LOG_BYTES).unwrap();
        drop(handle);
        fs::write(backup_log_path(&path, 1), b"previous").unwrap();

        rotate_log_if_needed(&path).unwrap();

        assert!(!path.exists());
        assert_eq!(
            fs::metadata(backup_log_path(&path, 1)).unwrap().len(),
            MAX_LOG_BYTES
        );
        assert_eq!(fs::read(backup_log_path(&path, 2)).unwrap(), b"previous");
        fs::remove_dir_all(root).unwrap();
    }
}
