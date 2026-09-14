class Agent:
    """Base Agent Implementation for AI Assistants."""
    def __init__(self, client, config, system=""):
        self.client = client
        self.system = system
        self.config = config
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        """Handle user input and generate a response."""
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        """Generate a response from the LLM."""
        try:
            completion = self.client.chat.completions.create(
                model=self.config.agent_model,
                temperature=self.config.temperature,
                messages=self.messages
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"