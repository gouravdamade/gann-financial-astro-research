# Clean Android 0.10.19 Candidate

Date: 2026-07-22

## Purpose

Replace the dirty-source Android `0.10.17` physical-test candidate before
collecting formal phone evidence. This avoids spending a complete MOB-01
through MOB-08 pass on an artifact that could not be promoted.

## Candidate

- release ID: `gann-astro-mobile-0.10.19-android-debug`;
- source commit: `3cabe251338ca143c70530b7fb40739d95c2d55e`;
- app source dirty: false;
- APK:
  `D:\GannFinancialAstro\mobile\release_candidate\GannAstroMobile-0.10.19-debug\GannAstroMobile-0.10.19-debug.apk`;
- bytes: 41,074,685;
- SHA-256:
  `A8D4D28F9EB4DC0DC0A672FE6B611019E1A7E4CA6B1EE5D7CB09890FC645F635`;
- execution allowed: false.

The packaging script used its checked-in copy-based Gradle fallback after the
expected Windows symlink restriction. Both Gradle clean and arm64 debug
assembly completed successfully.

## Verification

- frontend: 71 passed across 22 test files;
- backend: 117 passed;
- TypeScript/Vite production build: passed;
- Oxlint: passed;
- Rust library: 15 passed, 0 failed;
- Rust Clippy with `-D warnings`: passed;
- Android Rust compilation: passed;
- Gradle arm64 debug assembly: passed;
- manifest SHA equals independently computed APK SHA: passed;
- APK Signature Scheme v2: passed, one Android debug signer;
- package: `com.gouravdamade.gannastrodesk`;
- version code/name: `10019` / `0.10.19`;
- SDK range: minimum 24, target/compile 36;
- embedded `lib/arm64-v8a/libgann_astro_desk_lib.so`: present.

Detailed machine-readable evidence is in
`status/audits/android_clean_candidate_0_10_19_20260722.json`.

## Honest Limitations

- The phone was offline on Tailscale and no USB Android device was attached.
  No physical acceptance result was inferred from automated checks.
- MOB-01 through MOB-08 remain pending.
- The APK uses Android debug signing. It is suitable for the private physical
  acceptance pass, but not for production promotion.
- The Windows installer is also not code-signed.
- Vite chunk size, Gradle 9 compatibility, and generated Android API
  deprecation warnings are recorded as non-blocking build debt.

## Next Gate

1. Bring the phone online, install this exact APK, and collect hash-addressed
   evidence for MOB-01 through MOB-08.
2. Correct any physical defect and repeat only against a newly frozen artifact.
3. After behavioral acceptance, establish controlled Android release signing
   and Windows code signing, then rerun install/pairing smoke tests on the exact
   signed artifacts before any stable promotion.

## Recovery Snapshot

`D:\PycharmProjects\chat_session_backups\session_20260722_195204_android_clean_candidate_0_10_19`
