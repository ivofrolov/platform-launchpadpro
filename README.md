# Launchpad Pro: development platform for [PlatformIO](https://platformio.org/)

Develop your own firmware for the [Novation Launchpad Pro](https://novationmusic.com/launch/launchpad-pro) grid controller.

See the original [documentation](https://github.com/dvhdr/launchpad-pro) for API and hardware description.

## Getting Started

Install development platform.

    pio platform install https://github.com/ivofrolov/platform-launchpadpro.git

Create project.

    pio init -b launchpadpro

Compile and upload custom firmware to the Launchpad.

    pio run -t upload

Or restore original firmware.

    pio run -t restore

## Simulator

There is also a [native development platform](https://github.com/ivofrolov/platform-launchpadpro-simulator) to simplify firmware development using a desktop simulator.

You can combine both hardware platform and simulator in one project using Platformio environments.
