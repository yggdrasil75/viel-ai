from src.controller.config import queue_to_process_everything
import discord
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from src.controller.discordo import send

# GOD Refactoring this gonna be a bitch and a half...


async def think() -> None:

    while True:
        content = await queue_to_process_everything.get()
        message:discord.Message = content["message"]
        bot:AICharacter = content["bot"]
        dimension:Dimension = content["dimension"]

        try:
            await message.add_reaction('✨')
        except Exception as e:
            print("Hi!")

        message_content = str(message.content)

        if message_content.startswith("//"):
            pass
        else:
            await send_llm_message(bot,message,dimension, plugin="") # Prepping up to make plugins easier to handle, maybe
        queue_to_process_everything.task_done()

async def send_llm_message(bot: AICharacter,message:discord.message.Message,dimension:Dimension, plugin):
    print("The following is the content of message: \n\n" +str(message.author.display_name))
    dm=False
    prompter = PromptEngineer(bot,message,dimension)
    if isinstance(message.channel,discord.channel.DMChannel):
        dm = True
    queueItem = QueueItem(
        prompt=await prompter.create_text_prompt(),
        bot = bot.name,
        user = message.author.display_name,
        stop=prompter.stopping_string,
        prefill=prompter.prefill,
        dm=dm
        )
    print("Chat Completion Processing...")
    queueItem = await generate_response(queueItem)
    await send(bot,message,queueItem)
    return
