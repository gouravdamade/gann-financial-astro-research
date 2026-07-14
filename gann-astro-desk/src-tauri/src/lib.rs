use serde::Serialize;
use std::env;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::net::{IpAddr, Ipv4Addr, SocketAddr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant};
use tauri::{AppHandle, Manager, RunEvent, State};

const SIDECAR_CONTRACT: &str = "GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1";

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct BackendRuntimeInfo {
    contract: &'static str,
    base_url: String,
    port: u16,
    pid: u32,
    status: String,
    execution_allowed: bool,
}

struct BackendRuntimeState {
    info: BackendRuntimeInfo,
    child: Mutex<Option<Child>>,
}

enum SidecarLaunch {
    Executable(PathBuf),
    SourcePython { python: PathBuf, script: PathBuf },
}

fn available_port() -> Result<u16, String> {
    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0))
        .map_err(|error| format!("Unable to reserve a private backend port: {error}"))?;
    listener
        .local_addr()
        .map(|address| address.port())
        .map_err(|error| format!("Unable to read the private backend port: {error}"))
}

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

fn configure_hidden_process(command: &mut Command) {
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        command.creation_flags(CREATE_NO_WINDOW);
    }
}

impl BackendRuntimeState {
    fn spawn(app: &AppHandle) -> Result<Self, String> {
        let port = available_port()?;
        let codex_port = available_port()?;
        let launch = locate_sidecar(app)?;
        let data_root = default_data_root();
        let logs_dir = data_root.join("logs");
        fs::create_dir_all(&logs_dir)
            .map_err(|error| format!("Unable to create runtime logs: {error}"))?;
        let stdout = OpenOptions::new()
            .create(true)
            .append(true)
            .open(logs_dir.join("tauri_backend_sidecar.log"))
            .map_err(|error| format!("Unable to open backend sidecar log: {error}"))?;
        let stderr = OpenOptions::new()
            .create(true)
            .append(true)
            .open(logs_dir.join("tauri_backend_sidecar_error.log"))
            .map_err(|error| format!("Unable to open backend sidecar error log: {error}"))?;

        let mut command = match launch {
            SidecarLaunch::Executable(executable) => {
                let mut command = Command::new(&executable);
                if let Some(parent) = executable.parent() {
                    command.current_dir(parent);
                }
                command
            }
            SidecarLaunch::SourcePython { python, script } => {
                let mut command = Command::new(python);
                command.arg(&script);
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
            .env("GANN_ASTRO_DESKTOP_DATA", &data_root)
            .env("PYTHONUNBUFFERED", "1")
            .stdin(Stdio::piped())
            .stdout(Stdio::from(stdout))
            .stderr(Stdio::from(stderr));
        configure_hidden_process(&mut command);
        let child = command
            .spawn()
            .map_err(|error| format!("Unable to start managed backend sidecar: {error}"))?;
        let pid = child.id();

        Ok(Self {
            info: BackendRuntimeInfo {
                contract: SIDECAR_CONTRACT,
                base_url: format!("http://127.0.0.1:{port}"),
                port,
                pid,
                status: "starting".to_string(),
                execution_allowed: false,
            },
            child: Mutex::new(Some(child)),
        })
    }

    fn snapshot(&self) -> Result<BackendRuntimeInfo, String> {
        let mut info = self.info.clone();
        let mut child_guard = self
            .child
            .lock()
            .map_err(|_| "Backend sidecar state is unavailable".to_string())?;
        let child = child_guard
            .as_mut()
            .ok_or_else(|| "Backend sidecar is not running".to_string())?;
        if let Some(status) = child
            .try_wait()
            .map_err(|error| format!("Unable to inspect backend sidecar: {error}"))?
        {
            *child_guard = None;
            return Err(format!("Backend sidecar exited early with status {status}"));
        }
        let address = SocketAddr::new(IpAddr::V4(Ipv4Addr::LOCALHOST), info.port);
        info.status = if TcpStream::connect_timeout(&address, Duration::from_millis(120)).is_ok() {
            "ready"
        } else {
            "starting"
        }
        .to_string();
        Ok(info)
    }

    fn shutdown(&self) {
        let Ok(mut child_guard) = self.child.lock() else {
            return;
        };
        let Some(mut child) = child_guard.take() else {
            return;
        };
        if let Some(stdin) = child.stdin.as_mut() {
            let _ = stdin.write_all(b"shutdown\n");
            let _ = stdin.flush();
        }
        let deadline = Instant::now() + Duration::from_secs(8);
        while Instant::now() < deadline {
            match child.try_wait() {
                Ok(Some(_)) => return,
                Ok(None) => thread::sleep(Duration::from_millis(100)),
                Err(_) => break,
            }
        }
        let _ = child.kill();
        let _ = child.wait();
    }
}

#[tauri::command]
fn backend_runtime(state: State<'_, BackendRuntimeState>) -> Result<BackendRuntimeInfo, String> {
    state.snapshot()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .setup(|app| {
            let state = BackendRuntimeState::spawn(app.handle())?;
            app.manage(state);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![backend_runtime])
        .build(tauri::generate_context!())
        .expect("Gann Astro Desk failed to build");

    app.run(|app_handle, event| {
        if matches!(event, RunEvent::ExitRequested { .. } | RunEvent::Exit) {
            app_handle.state::<BackendRuntimeState>().shutdown();
        }
    });
}
