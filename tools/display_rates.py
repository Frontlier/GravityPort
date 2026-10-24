# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only SDL3 display/refresh-rate inspection for GravityPort."""
from __future__ import annotations
import ctypes as c
import json
from pathlib import Path
import os

class SDL_DisplayMode(c.Structure):
    _fields_=[("displayID",c.c_uint32),("format",c.c_uint32),
              ("w",c.c_int),("h",c.c_int),
              ("pixel_density",c.c_float),("refresh_rate",c.c_float),
              ("refresh_rate_numerator",c.c_int),
              ("refresh_rate_denominator",c.c_int),("internal",c.c_void_p)]

def inspect(path=r"C:\msys64\clang64\bin\SDL3.dll"):
    dll=c.CDLL(str(path))
    dll.SDL_Init.argtypes=[c.c_uint32];dll.SDL_Init.restype=c.c_bool
    dll.SDL_GetDisplays.argtypes=[c.POINTER(c.c_int)];dll.SDL_GetDisplays.restype=c.POINTER(c.c_uint32)
    dll.SDL_GetDisplayName.argtypes=[c.c_uint32];dll.SDL_GetDisplayName.restype=c.c_char_p
    dll.SDL_GetCurrentDisplayMode.argtypes=[c.c_uint32];dll.SDL_GetCurrentDisplayMode.restype=c.POINTER(SDL_DisplayMode)
    dll.SDL_GetFullscreenDisplayModes.argtypes=[c.c_uint32,c.POINTER(c.c_int)]
    dll.SDL_GetFullscreenDisplayModes.restype=c.POINTER(c.POINTER(SDL_DisplayMode))
    dll.SDL_free.argtypes=[c.c_void_p]
    dll.SDL_QuitSubSystem.argtypes=[c.c_uint32]
    flag=0x20
    if not dll.SDL_Init(flag):
        raise RuntimeError("SDL3 video initialization failed")
    result=[]
    try:
        count=c.c_int()
        ids=dll.SDL_GetDisplays(c.byref(count))
        if not ids:return result
        try:
            for i in range(count.value):
                ident=ids[i];name=dll.SDL_GetDisplayName(ident) or b"unnamed"
                current=dll.SDL_GetCurrentDisplayMode(ident)
                current_mode=None if not current else {
                    "resolution":f"{current.contents.w}x{current.contents.h}",
                    "hz":round(current.contents.refresh_rate,2)}
                n=c.c_int()
                modes=dll.SDL_GetFullscreenDisplayModes(ident,c.byref(n))
                items=[]
                if modes:
                    for j in range(n.value):
                        if modes[j]:
                            m=modes[j].contents
                            items.append((m.w,m.h,round(m.refresh_rate,2)))
                    dll.SDL_free(c.cast(modes,c.c_void_p))
                result.append({"name":name.decode("utf8","replace"),"current":current_mode,
                               "modes":sorted(set(items),key=lambda x:(x[0],x[1],x[2]))})
        finally:
            dll.SDL_free(c.cast(ids,c.c_void_p))
    finally:
        dll.SDL_QuitSubSystem(flag)
    return result

if __name__=="__main__":
    for item in inspect():
        selected=[x for x in item["modes"] if x[0]>=1280 and x[1]>=720]
        print(json.dumps({"display":item["name"],"current":item["current"],
                          "largest_hz":max([x[2] for x in item["modes"]],default=None),
                          "modes_720p_plus":selected[-35:]},ensure_ascii=False,indent=2))
