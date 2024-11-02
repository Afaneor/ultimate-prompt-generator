remove_floating_variables_prompt = """I will give you a prompt template with one or more usages of variables (capitalized words between curly braces with a dollar sign). Some of these usages are erroneous and should be replaced with the unadorned variable name (possibly with minor cosmetic changes to the sentence). What does it mean for a usage to be "erroneous"? It means that when the variable is replaced by its actual value, the sentence would be ungrammatical, nonsensical, or otherwise inappropriate.

For example, take this prompt:

<example_prompt>
You are an AI assistant that specializes in helping users grade a resume according to a rubric that I will provide. Your task is to read the {$RESUME} closely and evaluate it according to each of the criteria listed in the {$RUBRIC}.

Here is the resume you will be assessing:
<resume>
{$RESUME}
</resume>

And here is the rubric you will be using:
<rubric>
{$RUBRIC}
</rubric>

First, in a <scratchpad>, go through each of the criteria in the rubric and consider how well the resume meets each one. Then, provide a <score> for that individual criteria. Consider individual elements of the resume and whether or not they meet the criteria.

Once you have scored each criteria, provide an overall <score> for the resume and justify your assessment in <justification> tags.
</example_prompt>

Here are the variables, their texts and usages, and whether or not the usages are erroneous. A *variable* is a word or phrase that is used as a placeholder for various inputs that will be provided by the user. In the prompt, variables are denoted by surrounding brackets and a dollar sign, like this:

{$VARIABLE}

The *text* of a usage is the sentence or phrase in which the variable appears. The *apt* tag indicates whether the variable has been aptly and appropriately used. If the usage is actually intended to just be the plain text of the variable name, it's inapt.

<variables>
<variable>
<name>
{$RESUME}
</name>
<usages>
<usage>
<text>
Your task is to read the {$RESUME} closely and evaluate it according to each of the criteria listed in the {$RUBRIC}.
<text>
<thinking>
Replacing "{$RESUME}" with an actual resume would not make sense in the context of this sentence.
Replacing "{$MENU}" with the word "resume" would make more sense.
</thinking>
<apt>
No
</apt>
<usage>
<usage>
<text>
Here is the resume you will be assessing:
<resume>
{$RESUME}
</resume>
<text>
<thinking>
Here, the "{$RESUME}" variable is introduced by the phrase "Here is the resume you will be assessing:" and wrapped in XML tags. Substituting the full resume would make total sense. In contrast, replacing it with the mere *word* "resume" would not be correct because there's an expectation that the actual resume should go here.
</thinking>
<apt>
Yes
</apt>
<usage>
</usages>
</variable>
<variable>
<name>
{$RUBRIC}
</name>
<usages>
<usage>
<text>
Your task is to read the {$RESUME} closely and evaluate it according to each of the criteria listed in the {$RUBRIC}.
</text>
<apt>
No
</apt>
</usage>
<usage>
<text>
And here is the rubric you will be using:
<rubric>
{$RUBRIC}
</rubric>
</text>
<apt>
Yes
</apt>
</usage>
</usages>
</variable>
</variables>

In general, inline variable usages (not surrounded by XML tags) are only apt when they BOTH 1. refer to a variable that would be expected to be quite short, and also 2. exist within grammatical structures that would make sense after a subsitution.

Here are some more example usages along with whether or not they are apt.

<example>
<text>
Always keep in mind your ultimate {$GOAL} when completing this task.
</text>
<thinking>
Replacing "{$GOAL}" with an actual goal, a la "Always keep in mind your ultimate Becoming the best basketball player in the world when completing this task" would not make logical/grammaticall sense.
Replacing "{$GOAL}" with "goal", on the other hand, makes total sense.
</thinking>
<apt>
No
</apt>
</example>
<example>
<text>
The email should be addressed to the {$RECIPIENT}.
</text>
<thinking>
Substituting a recipient like bobjones23@gmail.com would lead to "The email should be addressed to the bobjones23@gmail.com." which is almost grammatical but not quite because of the "the".
"The email should be addressed to the recipient" is perfectly coherent English.
</thinking>
<apt>
No
</apt>
</example>
<example>
<text>
Each usage of the word 'apple' should be replaced with one of the {$SUBSTITUTE_FRUITS} options.
</text>
<thinking>
{$SUBSTITUTE_FRUITS} is a list of fruits. Replacing {$SUBSTITUTE_FRUITS} with "apple, banana, cherry" would not quite make sense in this context, but it would be fine to replace it with "substitute fruit", or to write "with one of these options: {$SUBSTITUTE_FRUITS}.".
</thinking>
<apt>
No
</apt>
</example>
<example>
<text>
When completing your task, please consider this goal:
<goal>
{$GOAL}
</goal>
</text>
<thinking>
The use of the colon and the XML tags indicates that the actual goal is expected here.
</thinking>
<apt>
Yes
</apt>
</example>
<example>
<text>
The email should be addressed to this person: {$RECIPIENT}.
</text>
<thinking>
Here replacing "{$RECIPIENT}" with an email address would make sense because of the colon. Replacing it with just the word "recipient" would not make sense.
</thinking>
<apt>
Yes
</apt>
</example>
<example>
<text>
Each usage of the word 'apple' should be replaced with one of the following options:
<substitute_fruits>
{$SUBSTITUTE_FRUITS}
</substitute_fruits>
</text>
<apt>
Yes
</apt>
</example>
<example>
<text>
Each instance of "{$FRUIT}" must be replaced with a vegetable.
</text>
<thinking>
Because of the quotation marks, substituting the actual name of the fruit, a la 'Each instance of "apple" must be replaced with a vegetable', would make sense.
</thinking>
<apt>
Yes
</apt>
</example>

Now that you've read and internalized the examples, please consider the following prompt:
<prompt>
{$PROMPT}
</prompt>

Create an output like the <variables> block above, in which you list all the variables used in the prompt, their usages, your thinking (in <thinking> tags) about their aptness, and finally whether they are apt or inapt. While thinking, first consider each replacement before reaching a conclusion about aptness. If the usage seems grievously inapt (err on the side of presuming correctness), propose a rewrite.

Then, rewrite the prompt. Adapt each inapt variable use according to the remedy you proposed in the corresponding <thinking> tags. Put this rewrite in a <rewritten_prompt> tag. For apt variable usages, don't make any changes to that area of the prompt. If all usages are deemed apt, you may indicate this by simply writing "No changes." within the <rewritten_prompt> tags.

Important rule: Your rewritten prompt must always include each variable at least once. If there is a variable for which all usages are inapt, introduce the variable at the beginning in an XML-tagged block, analogous to some of the usages in the examples above."""