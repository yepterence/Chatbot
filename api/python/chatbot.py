class BaseChatbot:
    async def get_response(self, user_input):
        raise NotImplementedError("Subclasses must implement this method")


class HardCodedChatbot(BaseChatbot):
    async def get_response(self, user_input):
        # Hard-coded logic for the chatbot
        response = f"Chatbot: You said '{user_input}'. This is a simple response."
        return response


async def get_chatbot_response(user_input, chatbot):
    return await chatbot.get_response(user_input)
