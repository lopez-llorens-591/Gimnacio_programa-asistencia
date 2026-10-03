from ui import iniciar_ui
from iniciador import inicializador
import asyncio


async def main():
    await inicializador()
    iniciar_ui()

if __name__ == "__main__":
    asyncio.run(main())