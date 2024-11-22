from openai import OpenAI
import json
import time

client = OpenAI()


file = client.files.create(
  file=open("dataset.csv", "rb"),
  purpose='assistants'
)


assistant = client.beta.assistants.create(
  name="Fav City",
   instructions="""Always provide detailed outputs, including all available information, without summarization.  Do not omit details unless explicitly asked by the user. 
Use the 'favourite_city_and_why' column for identifying the reasoning behind each person's favorite city. 'name' column gives the names of persons.""",
  model="gpt-4o",
  tools=[{"type": "code_interpreter"}],
  tool_resources={
    "code_interpreter": {
      "file_ids": [file.id]
    }
  }
)

thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Which city Tina Escobar enjoys most ? List the full reason why she enjoys it, without summarizing or omitting any details. Show the raw data before processing first and then show your response",
      "attachments": [
        {
          "file_id": file.id,
          "tools": [{"type": "code_interpreter"}]
        }
      ]
    }
  ]
)

try:
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        max_completion_tokens=2000,
        max_prompt_tokens=10000
    )
except Exception as e:
    print(f"Error creating run: {e}")
    raise


while True:
    try:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            print("Run completed successfully:")
            print(messages)
            break
        elif run.status == 'failed':
            print("Run failed. Details:")
            print(run)  # Inspect the full run object for error details
            break
        else:
            print(f"Current status: {run.status}")
            time.sleep(2)  # Reduce polling frequency
    except Exception as e:
        print(f"Error while checking run status: {e}")
        raise

