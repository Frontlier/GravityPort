/* SPDX-License-Identifier: GPL-2.0-or-later
 * GravityPort.exe: desktop-friendly direct launcher, derived from the original
 * Gravity Rush PC packaging/windows/play.c. Preserves the native launcher
 * process tree and waits for gameplay to exit.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wchar.h>

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR arguments, int show)
{
    (void)instance; (void)previous; (void)show;
    wchar_t dir[32768], exe[32768], line[32768];
    DWORD length = GetModuleFileNameW(NULL, dir, 32768);
    if (length == 0 || length >= 32768) return 1;
    wchar_t *slash = wcsrchr(dir, L'\\');
    if (!slash) return 2;
    *slash = 0;
    if (swprintf(exe, 32768, L"%ls\\GravityPort Launcher.exe", dir) < 0) return 3;
    if (swprintf(line, 32768, L"\"%ls\" --play%ls%ls",
                 exe, arguments && *arguments ? L" " : L"",
                 arguments ? arguments : L"") < 0) return 4;
    STARTUPINFOW startup = {.cb = sizeof(startup)};
    PROCESS_INFORMATION process;
    if (!CreateProcessW(exe,line,NULL,NULL,FALSE,0,NULL,dir,&startup,&process)) {
        MessageBoxW(NULL,L"GravityPort Launcher.exe nao foi encontrado nesta pasta.",
                    L"GravityPort",MB_OK | MB_ICONERROR);
        return 1;
    }
    CloseHandle(process.hThread);
    WaitForSingleObject(process.hProcess,INFINITE);
    DWORD code=0;
    GetExitCodeProcess(process.hProcess,&code);
    CloseHandle(process.hProcess);
    return (int)code;
}
