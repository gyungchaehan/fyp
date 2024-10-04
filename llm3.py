# i am a coding machine

import ollama
import json

article = """
edition.cnn.com
Oil price surge is the No. 1 threat to the US economy, Moody’s economist warns | CNN Business
Matt Egan
6–7 minutes

New York CNN  —

The US jobs market is on fire. Consumer spending is strong. And the economy is growing at a brisk pace.
But there is a growing threat to that sunny economic backdrop: surging oil prices.
US oil prices are rapidly approaching $90 a barrel. Global oil prices are flirting with $92 a barrel amid worries about a wider war in the Middle East. And this has lifted gasoline prices to their highest levels in five months.
The risk is oil prices keep climbing, hurting consumer spending and undoing the meaningful progress on inflation. That could cause the Federal Reserve to delay interest rate cuts and spook investors on Wall Street.
“It’s the most serious threat to the economy,” Moody’s chief economist Mark Zandi told CNN in a phone interview. “Nothing does more damage to the economy more quickly than higher oil prices.”
Not only that, but enormous political consequences could follow if gasoline prices spike above $4 a gallon and stay there.
Moody’s published a model earlier this year that showed gas prices are a key variable in the November election, one that could tip the scales in the favor of former President Donald Trump.
“If they go above $4 a gallon for more than two or three months, Trump will win,” Zandi said.
US oil prices surged above $87 a barrel late last week for the first time since late October, leaving them up about 21% this year.
“We can digest $85 or $90 oil. If we go over $90 and closer to $100, that’s a problem,” Zandi said. “Consumers are going to get nailed – especially lower-income households. And it undermines confidence. People look at the price of gas as a litmus test for their own financial situation.”
This oil price rally has been driven in large part by war.
First, drone attacks on oil refineries deep inside Russia helped lift oil prices last month.
Now, the focus is on the Middle East and how Iran will respond to last week’s deadly airstrike on its embassy complex in Syria.
Iranian officials have vowed to retaliate against Israel, which hasn’t claimed responsibility for the attack but has argued that the target was a “military building of Quds forces” — a unit of the Iranian Revolutionary Guards responsible for foreign operations.
“The probability of a supply disruption is rising. There is a fear of a retaliatory strike that could lead to a disruption,” said Andy Lipow, president of Lipow Oil Associates. “It’s very easy to see $95 Brent. If another geopolitical event occurs in the Middle East, $100 Brent is not out of the question.”
Helima Croft, a former CIA analyst who is now global head of commodity strategy at RBC Capital Markets, told clients in a note that there is a risk that this “tit-for-tat cycle expands into a wider conflict than what some of the key stakeholders are seeking.”
Joe Brusuelas, chief economist at RSM, said the “greatest external risk to the US economy is geopolitical tensions in the Middle East” because they would boost oil and gasoline prices.
“Combined they are the only thing in the near term that could cause an end to the current business cycle,” Brusuelas said.
However, Brusuelas said oil prices would have to spike much higher – to around $115 to $130 per barrel – before it raises the specter of a recession.
Gas prices climbed to $3.58 a gallon on average nationally on Friday, according to AAA. That’s up four cents in a week and 21 cents in a month.
Beyond the Middle East tensions, oil and gas prices have been boosted by OPEC and its allies, which continue to restrain supply.
Strong seasonal factors also are at at play. Gasoline prices typically rise in the spring as refineries switch over to more expensive summer fuel and as more people hit the roads, boosting demand.
The higher gas prices go, the worse upcoming inflation readings will look. Fed officials will be combing through the next few inflation reports very closely as they debate whether to cut interest rates in June.
Vincent Reinhart, a former Fed economist who is now chief economist at Dreyfus and Mellon, told CNN the risk to inflation is on the upside because of goods prices, including commodities.
“Commodity prices matter a lot. That could dislodge the favorable goods price developments,” Reinhart said. “Oil prices in particular really resonate with households. They oversample with that.”
Reinhart thinks the Fed will cut interest rates in June, in part because officials will want to get ahead of the election season when their strategy will be subject to more intense political scrutiny.
“The election season is going to just get more toxic,” he said. “For the Fed to change the course of policy right in the runup to the election after the national conventions is just going to call a lot of attention to it and call into question its policy intent.”
The good news is that despite the growing risks, some energy market veterans are standing by their cautiously optimistic forecasts.
Lipow expects the national average to climb toward $3.70 a gallon in the coming weeks, but he’s still not calling for $4 a gallon.
Patrick De Haan, head of petroleum analysis at GasBuddy, told CNN that he is still expecting gas prices to average in the upper-$3 range unless a major hurricane damages US refineries.
“I still don’t think a $4 a gallon national average is imminent,” De Haan said.
"""

response = ollama.chat(model='llama3.2',
    messages=[
        {
            'role': 'user',
            'content': f"""You are a global finance expert. You are asked to provide a
            correlation score based on how much the REAL LIFE EVENTS that are discussed article impacts oil price movement;
            positive one being perfect correlation of upward price motion, negative one meaning the opposite.
            Only focus on the actual events and their impact on oil prices, not the article's opinion or content.
            Provide a json with key "score" and a float value between -1 and 1, and a reasoning.
            \n
            Article content: {article}
            """,
        },
    ],
    format='json'
)

result = json.loads(response['message']['content'])
print(result["score"])
