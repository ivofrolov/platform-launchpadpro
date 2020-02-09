from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment


env = DefaultEnvironment()

PLATFORM_DIR = env.PioPlatform().get_dir()

env.Replace(
    CC='arm-none-eabi-gcc',
    OBJCOPY='arm-none-eabi-objcopy',
    LDSCRIPT_PATH=join(PLATFORM_DIR, 'ld/stm32_flash.ld'),
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
    PROGNAME='launchpad_pro',
    HEXTOSYX=join(PLATFORM_DIR, 'tools/hextosyx.py')
)

env.Append(
    LIBS=[
        File(join(PLATFORM_DIR, 'lib/launchpad_pro.a'))
    ],
    CPPPATH=[
        join(PLATFORM_DIR, 'include')
    ]
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
                '${HEXTOSYX}',
                '$SOURCES',
                '$TARGET'
            ]), 'Building $TARGET'),
            suffix='.syx'
        )
    )
)

if 'nobuild' in COMMAND_LINE_TARGETS:
    target_elf = join('$BUILD_DIR', '${PROGNAME}.elf')
    target_hex = join('$BUILD_DIR', '${PROGNAME}.hex')
    target_syx = join('$BUILD_DIR', '${PROGNAME}.syx')
else:
    target_elf = env.BuildProgram()
    target_hex = env.ElfToHex(join('$BUILD_DIR', '${PROGNAME}'), target_elf)
    target_syx = env.HexToSyx(join('$BUILD_DIR', '${PROGNAME}'), target_hex)

AlwaysBuild(env.Alias('nobuild', target_syx))

Default(target_syx)
