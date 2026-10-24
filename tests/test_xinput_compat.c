/* Regression for Xbox/XInput without physical gyro or touchpad. */
#define _GNU_SOURCE
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../src/runtime_pad.c"

int gow3gpu_overlay_captures_input(void) { return 0; }
void gow3gpu_choice_set_input(uint32_t (*buttons)(void)) { (void)buttons; }
uintptr_t runtime_lookup(const RuntimeExport *table, size_t count, const char *name) {
    (void)table; (void)count; (void)name;
    return 0;
}

int main(void) {
    _putenv_s("GOW3_GYRO_STICK", "1");
    _putenv_s("GOW3_XINPUT_TOUCHPAD", "1");
    _putenv_s("SDL_VIDEODRIVER", "dummy");
    SDL_SetHint(SDL_HINT_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT, "0x1d50/0x6189");
    assert(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMEPAD));
    SDL_VirtualJoystickDesc desc;
    SDL_INIT_INTERFACE(&desc);
    desc.type=SDL_JOYSTICK_TYPE_GAMEPAD;
    desc.naxes=SDL_GAMEPAD_AXIS_COUNT;
    desc.nbuttons=SDL_GAMEPAD_BUTTON_COUNT;
    desc.button_mask=(1u<<SDL_GAMEPAD_BUTTON_COUNT)-1;
    desc.axis_mask=(1u<<SDL_GAMEPAD_AXIS_COUNT)-1;
    desc.name="Gravity Rush XInput regression";
    desc.vendor_id=0x1d50;
    desc.product_id=0x6189;
    SDL_JoystickID id=SDL_AttachVirtualJoystick(&desc);
    assert(id);
    SDL_Joystick *joy=SDL_OpenJoystick(id);
    assert(joy);
    assert(pad_init()==0 && pad_open(1,0,0,NULL)==1);
    PadData data;
    assert(pad_read_state(1,&data)==0 && gamepad);
    assert(!motion.gyro);

    assert(SDL_SetJoystickVirtualButton(joy,SDL_GAMEPAD_BUTTON_BACK,true));
    assert(SDL_SetJoystickVirtualButton(joy,SDL_GAMEPAD_BUTTON_DPAD_RIGHT,true));
    SDL_UpdateJoysticks(); SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0);
    assert((data.buttons & BTN_TOUCHPAD) && !(data.buttons & BTN_RIGHT));
    assert(data.touch_count==1 && data.touches[0].x==1440);
    assert(SDL_SetJoystickVirtualButton(joy,SDL_GAMEPAD_BUTTON_DPAD_RIGHT,false));
    SDL_UpdateJoysticks(); SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0);
    assert(data.touch_count==1 && data.touches[0].x==480);
    assert(SDL_SetJoystickVirtualButton(joy,SDL_GAMEPAD_BUTTON_BACK,false));

    assert(SDL_SetJoystickVirtualButton(joy,SDL_GAMEPAD_BUTTON_LEFT_STICK,true));
    SDL_UpdateJoysticks(); SDL_UpdateGamepads();
    assert(pad_read_state(1,&data)==0);
    assert((data.buttons & BTN_L3)); /* L3 alone still works. */
    assert(SDL_SetJoystickVirtualAxis(joy,SDL_GAMEPAD_AXIS_RIGHTX,27000));
    for (int i=0;i<14;i++) {
        SDL_UpdateJoysticks(); SDL_UpdateGamepads();
        SDL_Delay(18);
        assert(pad_read_state(1,&data)==0);
    }
    assert(!(data.buttons & BTN_L3)); /* Combo is consumed, not sent to game. */
    assert(data.right_x==128 && data.right_y==128);
    assert(fabsf(data.orientation[1]) > 0.03f);
    assert(fabsf(data.angular_velocity[1]) > 0.05f);
    printf("PASS: XInput fallback gyro yaw=%.3f, touch right/left, ordinary L3 kept\n",data.orientation[1]);

    SDL_CloseJoystick(joy);
    if (gamepad) SDL_CloseGamepad(gamepad);
    gamepad=NULL;
    assert(SDL_DetachVirtualJoystick(id));
    SDL_Quit();
    return 0;
}
