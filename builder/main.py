from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment


env = DefaultEnvironment()

PLATFORM_DIR = env.PioPlatform().get_dir()

env.Replace(
    AR="arm-none-eabi-gcc-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-gcc-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],

    LDSCRIPT_PATH=join(PLATFORM_DIR, 'ld/stm32_flash.ld'),

    PROGNAME='launchpad_pro',
    PROGSUFFIX=".elf",

    SIZEPROGREGEXP=r"^(?:\.text|\.data|\.rodata|\.text.align|\.ARM.exidx)\s+(\d+).*",
    SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
    SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
    SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',

    HEXTOSYX=join(PLATFORM_DIR, 'tools/hextosyx.py'),
    SENDSYSEX=join(PLATFORM_DIR, 'tools/sendsysex.py'),
)

env.Append(
    CCFLAGS=[
        '-Os',
        '-Wall',
        '-D_STM32F103RBT6_',
        '-D_STM3x_',
        '-D_STM32x_',
        '-mthumb',
        '-mcpu=cortex-m3',
        '-fsigned-char',
        '-DSTM32F10X_MD',
        '-DUSE_STDPERIPH_DRIVER',
        '-DHSE_VALUE=6000000UL',
        '-DCMSIS',
        '-DUSE_GLOBAL_CONFIG',
        '-ffunction-sections',
        '-std=c99',
        '-mlittle-endian'
    ],
    LINKFLAGS=[
        '-u',
        '_start',
        '-u',
        '_Minimum_Stack_Size',
        '-mcpu=cortex-m3',
        '-mthumb',
        '-specs=nano.specs',
        '-specs=nosys.specs',
        '-nostdlib',
        '-Wl,-static',
        '-N',
        '-nostartfiles',
        '-Wl,--gc-sections'
    ],
    LIBS=[
        File(join(PLATFORM_DIR, 'lib/launchpad_pro.a'))
    ],
    CPPPATH=[
        join(PLATFORM_DIR, 'include')
    ],
)

env.Append(
    BUILDERS=dict(
        ElfToHex=Builder(
            action=env.VerboseAction(' '.join([
                '$OBJCOPY',
                '-O',
                'ihex',
                '$SOURCES',
                '$TARGET'
            ]), 'Building $TARGET'),
            suffix='.hex'
        ),
        HexToSyx=Builder(
            action=env.VerboseAction(' '.join([
                'python3',
                '$HEXTOSYX',
                '$SOURCES',
                '$TARGET'
            ]), 'Building $TARGET'),
            suffix='.syx'
        ),
    ),
)

# Target: Build

if 'nobuild' in COMMAND_LINE_TARGETS:
    target_elf = join('$BUILD_DIR', '${PROGNAME}.elf')
    target_hex = join('$BUILD_DIR', '${PROGNAME}.hex')
    target_syx = join('$BUILD_DIR', '${PROGNAME}.syx')
else:
    target_elf = env.BuildProgram()
    target_hex = env.ElfToHex(join('$BUILD_DIR', '${PROGNAME}'), target_elf)
    target_syx = env.HexToSyx(join('$BUILD_DIR', '${PROGNAME}'), target_hex)

AlwaysBuild(env.Alias('nobuild', target_syx))

# Target: Print binary size

target_size = env.Alias(
    'size',
    target_elf,
    env.VerboseAction('$SIZEPRINTCMD', 'Calculating size $SOURCE'),
)

AlwaysBuild(target_size)

# Target: Upload

env.Replace(
    UPLOAD_PORT='"Launchpad Pro"'
)

upload = env.VerboseAction(' '.join([
    'python3',
    '$SENDSYSEX',
    '-p',
    '$UPLOAD_PORT',
    '$SOURCE'
]), 'Uploading $SOURCE')

env.AddPlatformTarget(
    'upload',
    target_syx,
    upload,
    'Upload',
    'Send firmware to Launchpad Pro over MIDI',
)

# Target: Restore

env.AddPlatformTarget(
    'restore',
    join(PLATFORM_DIR, 'resources/Launchpad Pro.syx'),
    upload,
    'Restore',
    'Restore Launchpad Pro original firmware',
)

# Default Targets

Default([target_syx, target_size])

# Requirements

try:
    import intelhex
except ImportError:
    env.Execute('$PYTHONEXE -m pip install intelhex==2.3.0')

try:
    import rtmidi
except ImportError:
    env.Execute('$PYTHONEXE -m pip install python-rtmidi==1.4.9')
