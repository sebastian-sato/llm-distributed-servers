import llm
import random

'''
The purpose of this module is to prevent memory errors from occuring by attempting to determine a (rather conservative) estimate of the largest
amount of characters the model can accept without any risk of a memory error occuring.

Those among you who are familiar with how LLMs work might rightly point out that this doesn't really make sense, as LLMs use tokens, not characters.
Character count is used because, while in practice a string constructed in proper english will use fewer tokens than a string of random characters,
a string of random characters represents something close to the maximum amount of tokens that can be packed into a string of size n, and thus character 
count makes for a useful lower bound estimate of what the model can handle, as getting the actual token count of a string may not be easy to do in all cases.

While it is possible to determine a more accurate estimate of an LLMs maximum resource usage, given any arbitrary prompt, directly based on its architecture, 
this assumes that the model's internal workings are exposed and able to be accessed directly, which might not be convenient, or even possible, with all APIs
and libraries.

As such, this is meant to be as general and safe as possible. Though note that there is one line towards the bottom, the definition of 'structured_prompt',
that may need to change depending on what model is used. I couldn't really think of a good way to abstract it out of this file so just keep that in mind.
'''

INSTRUCTION = "This is a resource usage test, please output 500 occurences of the word \"the\", without any commentary. Ignore the random text.\n\n"
ASSUMED_INSTRUCTION_TOKEN_LENGTH = 30 # Reasonable rough estimate for most tokenizers? Someone tell me if I'm dead wrong cuz i didn't check :P

WRITE_RESULT_TO_PATH = "./max-prompt-character-count.txt"

def get_resource_profile(iterations=5):
    try:
        with open(WRITE_RESULT_TO_PATH, "r") as f:
            print("Reading max character count from file.")
            value = int(f.read())
    except FileNotFoundError:
        print("Performing binary search to determine maximum safe character length for prompts.")
        _profile(iterations)
        with open(WRITE_RESULT_TO_PATH, "r") as f:
            value = int(f.read())
    return value

def _profile(iterations):
    safe_amount = _run_tests(iterations)
    with open(WRITE_RESULT_TO_PATH, "w") as f:
        f.write(str(safe_amount))
    print("Result saved to disk.")

def _run_tests(iterations):
    current = int(llm.MAXIMUM_CONTEXT_LENGTH - 100)
    last_success = -1
    maximum = current
    magnitude = int(current / 2)

    for i in range(iterations):
        print("Testing with ~" + str(current) + " tokens.")
        prompt = generate_test_prompt(current)
        try:
            response = llm.generate(prompt, 500)
            last_success = current
            current += magnitude
            if current > maximum:
                return maximum
        except Exception as e:
            #print("Exception caught during LLM inference:",e) # Useful for debugging but generally prints huge walls of text
            current -= magnitude
        magnitude = int(magnitude / 2)

    if last_success == -1:
        raise Exception("Testing failed, ensure your system has enough resources. If that's not the problem, then something might be wrong with your LLM implementation?")

    print("Determined",last_success,"to be a good conservative estimate for maximum character count.")
    return last_success

def generate_test_prompt(length):
    # Generate a hyper token dense prompt of random characters, so that each character will tend to translate to exactly one token.
    # This gives us a conservative but safe estimate.
    chars = list("abcdefghijklmnopqrstuvwxyz")
    assert length > ASSUMED_INSTRUCTION_TOKEN_LENGTH, "Length must be more than " + str(ASSUMED_INSTRUCTION_TOKEN_LENGTH)
    random_gibberish = ""
    for i in range(length-ASSUMED_INSTRUCTION_TOKEN_LENGTH):
        random_gibberish += random.choice(chars)
    prompt = INSTRUCTION + random_gibberish

    structured_prompt = [{"role":"user","content":prompt}] # POSSIBLY MODEL DEPENDENT!
    
    return structured_prompt

if __name__ == "__main__":
    profile()
