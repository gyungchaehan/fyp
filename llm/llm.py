from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

model_name = "deepset/roberta-base-squad2"

# a) Get predictions
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name, device="cpu")

context = """
Russia captures key town of Vuhledar in eastern Ukraine
Al Jazeera
3–4 minutes

Mining town located on strategic high ground links eastern and southern fronts, acts as supply hub for both sides.

Russia’s army has taken full control of the strategic hilltop town of Vuhledar in eastern Ukraine.

Ukraine’s military confirmed on Wednesday that it was withdrawing troops from the frontline town, which occupies a key location in the Donetsk region, to “protect the military personnel and equipment”.

As a result of the enemy’s actions, there arose a threat of encircling the city,” said the military’s Khortytsia ground forces formation in a statement posted on Telegram.

“Flanking attacks” had, it said, “exhausted” Ukrainian troops.

The withdrawal comes a day after the governor of Donetsk – one of the four Ukrainian regions Russia annexed in 2022 despite not being in full control of its territory – reported that Russian troops had reached the centre of Vuhledar.

Located on strategic high ground, the town has resisted capture since Russia launched its full-scale invasion in 2022.

Sign up for Al Jazeera
Weekly Newsletter

The latest news from around the world. Timely. Accurate. Fair.

A supply hub for both sides in the war, the town is located at the intersection of the eastern and southern fronts. Its capture has long been seen by Moscow as offering a major step towards incorporating the entire Donetsk region.

Vuhledar’s strategic importance is further heightened by its proximity to a rail line connecting Crimea – the Black Sea peninsula annexed by Russia in 2014 – to the industrial Donbas region, which comprises Donetsk and Luhansk regions, most of which Moscow controls.

While Ukrainian forces were in full control of Vuhledar, they were able to use the town as a platform to shell Russian military supply lines in the area.
A satellite view of Vuhledar
A satellite view of Vuhledar in Donetsk region, Ukraine, September 21, 2022 [Reuters]
Trapped

Russian forces reached the outskirts of the town last week and intensified their offensive push in recent days, trapping Ukrainian forces and complicating supplies and troop rotation.

The military bloggers claim that the remaining Ukrainian defenders were bombarded with devastating aerial glide bombs.

Fierce fighting since 2022 has left much of the town devastated.

On Tuesday, footage posted to social media showed Russian soldiers waving a flag from atop a bombed-out multistorey building and unfurling another flag on a metal spire on a roof.

The footage matched street patterns of Vuhledar, according to the news agency Reuters.

“The enemy is already nearly in the centre of the city,” Donetsk Governor Vadym Filashkin told Ukrainian TV on Tuesday.

Since August, Moscow’s troops in eastern Ukraine have advanced at their fastest rate in more than two years, with little letup, despite Ukrainian forces mounting a surprise incursion into Russia’s Kursk region.
"""


QA_input = {
    'question': 'Based on this article, give a score between negative one and positive one, indicating either a positive correlation between the article context and oil price increase, or negative if otherwise. As the number gets closer to one, it signals perfect correlation.',
    'context': context
}
res = nlp(QA_input)

# b) Load model & tokenizer
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
