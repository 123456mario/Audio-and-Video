import asyncio
from behringer_mixer import mixer_api

async def main():
    mixer = mixer_api.create("WING", ip="192.168.1.11", logLevel="WARNING")  # Wing IP 변경
    await mixer.start()
    state = await mixer.reload()
    print("Mixer State:", state)
    await mixer.stop()

if __name__ == "__main__":
    asyncio.run(main())
