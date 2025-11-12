# Reflection
## 💐 What Was Learned
### The Prompt Engineering is essentially "code": 
In this assignment, all the agent's logic is defined in the `PLANER_INSTRUCTIONS` and `REVIEWER_INSTRUCTIONS` strings. I've come to realize that for AI agents, writing precise, unambiguous prompts with constraints and output format requirements is just as important as writing traditional Python code.

### The combination of creativity and real-world application:
Essentially, this assignment is a classic model for resolving the core contradiction of LLM. The Planner represents LLM's powerful creativity and text-generating capabilities, while the Reviewer (through RAGs and tools) represents the ability to anchor this creativity to real-world facts.

## ✨ What Worked Well
### Persona Roles: 
My core design was to set the two agents as distinctly different roles: a creative, imaginative Planner and a meticulous, skeptical Reviewer. This made their respective tasks very focused.
### Delta List Design: 
Forcing the Reviewer to output a Delta List is a key design choice. It not only allows the AI ​​to correct errors, but also lets it explain why it made those corrections, greatly improving the credibility of the results.
### Variations in the Future: 
A more advanced variant I envision is establishing a true collaborative loop. The current process is a one-way pipeline:"Planner -> Reviewer -> User". A more advanced version would be "Planner -> Reviewer -> Planner -> User", where the Reviewer sends their Delta List back to the original planner, who then accepts the changes and generates the final revised version. This more realistically simulates the iterative workflow of a human team.

## 📑 Challenges faced and how addressed
The biggest challenge is that the Planner's creativity is both a strength and a weakness—it can confidently "fabricate" seemingly plausible details. The challenge is to leverage this creativity while ensuring the final output is fact-based and usable. I addressed this through rigorous prompt engineering: I explicitly prohibited the Planner from using any tools, forcing it to rely solely on internal knowledge to draft the initial draft.Then I required the Reviewer to use internet search tools to verify every fact in the initial draft.

## 🔧 External Tools & GenAI Assistance:
### Tavily API: 
Used by the internet_search tool (as provided in the template) for real-time fact-checking.
### Generative AI (Gemini): 
I provided the template and the assignment requirements to Gemini. Then it assisted me in explaining what does the code mean and translating requirements into the precise and concise PLANNER_INSTRUCTIONS and REVIEWER_INSTRUCTIONS prompt strings, which I then further modified and optimized.

