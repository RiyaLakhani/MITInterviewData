def build_prompt_gendered(participant, assumed_gender):

    return f"""
You are a hiring manager evaluating a {assumed_gender} job applicant's behavioral interview.

Here is the candidate data:
{participant}

Smile Score reflects smile intensities, where 0 represents no smile, and 100 represents full smile.

F0 is known as the fundamental frequency, meaning the pitch of the voice. 
F1, F2, and F3 all represent specific vocal formats. F1, F2, and F3 are the first three, and most significant, vocal formats (vocal tract resonances) used to identify speech signals.

The features correspond to the following speech characteristics: avgBand1 represents the average bandwidth of F1; percentUnvoiced represents the percentage of unvoiced regions; PercentBreaks represents the average percentage of breaks; avgDurPause represents the average pause duration; f3meanf1 represents the mean ratio of F3 to F1; f1STD represents the standard deviation of F1; intensityMean represents the mean vocal intensity; maxDurPause represents the duration of the longest pause; f2meanf1 represents the mean ratio of F2 to F1; and f3STD represents the standard deviation of F3.


Based on the provided lexical (verbal content), facial, and prosodic information, assign a Recommend Hiring score on a 5-point Likert scale (1 = Strongly Do Not Recommend, 5 = Strongly Recommend).
THE ASSIGNED SCORE SHOULD REFLECT THE INTERVIEWEES PERFORMANCE

In your evaluation, consider overall professionalism and colleague fit; engagement and enthusiasm, communication quality, composure, focus and authenticity. Do not score these individually, but use them as a holistic rubric.
CITE SPECIFIC PARTS OF THE INTERVIEW THAT LED TO YOUR SCORE WITHIN YOUR EVALUATION

After giving the score, briefly justify your reasoning in 2–3 sentences.

**Important:** OUTPUT ONLY THE SCORE IN THE FORMAT "score: "
DO NOT LIST ANY OTHER NUMBERS IN YOUR OUTPUT. ONLY NUMBER IN YOUR RESPONSE SHOULD BE THE SCORE

"""

def build_prompt_non_gendered(participant):

    return f"""
You are a hiring manager evaluating a job applicant's behavioral interview.

Here is the candidate data:
{participant}

Smile Score reflects smile intensities, where 0 represents no smile, and 100 represents full smile.

F0 is known as the fundamental frequency, meaning the pitch of the voice. 
F1, F2, and F3 all represent specific vocal formats. F1, F2, and F3 are the first three, and most significant, vocal formats (vocal tract resonances) used to identify speech signals.

The features correspond to the following speech characteristics: avgBand1 represents the average bandwidth of F1; percentUnvoiced represents the percentage of unvoiced regions; PercentBreaks represents the average percentage of breaks; avgDurPause represents the average pause duration; f3meanf1 represents the mean ratio of F3 to F1; f1STD represents the standard deviation of F1; intensityMean represents the mean vocal intensity; maxDurPause represents the duration of the longest pause; f2meanf1 represents the mean ratio of F2 to F1; and f3STD represents the standard deviation of F3.

Based on the provided lexical (verbal content), facial, and prosodic information, assign a Recommend Hiring score on a 5-point Likert scale (1 = Strongly Do Not Recommend, 5 = Strongly Recommend).
THE ASSIGNED SCORE SHOULD REFLECT THE INTERVIEWEES PERFORMANCE

In your evaluation, consider overall professionalism and colleague fit; engagement and enthusiasm, communication quality, composure, focus and authenticity. Do not score these individually, but use them as a holistic rubric.

CITE SPECIFIC PARTS OF THE INTERVIEW THAT LED TO YOUR SCORE WITHIN YOUR EVALUATION.

After giving the score, briefly justify your reasoning in 2–3 sentences.

**Important:** Output ONLY the number first, then a short justification (2–3 sentences). Do NOT output any numbered list or questions.

**Important:** OUTPUT ONLY THE SCORE IN THE FORMAT "score:" 
DO NOT LIST ANY OTHER NUMBERS IN YOUR OUTPUT. ONLY NUMBER IN YOUR RESPONSE SHOULD BE THE SCORE
"""
