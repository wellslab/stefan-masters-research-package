


# Ground truth data


Function to lookup ontology IDs and get term names
- i_source_cell_origin_id
- i_source_cell_type_id

Model is going to output term names. Need this function for scoring things.






## Missing data

- Really unprofessional how there are inconsistent values for missing data.
- Need to stick to a string 'None' or 'Missing'
- It makes it really hard to work with and these are meant to be IT professionals. I just don't understand. It's pure laziness.



# Filtering out the ground truth data


Need to filter out cell lines which appear in more than one publication.
This confounds test results. Some cell lines had pluripotency characterisation data that were from multiple publications. There was no link saying which publication which pluripotency characterisation data came from. Therefore these cell lines needed to be excluded.


# Choosing gpt models.

By the way, all of these models can be used with image inputs. Including pdf inputs.
So why was I even considering transcribing them in the first place? There was OCR technology available at the time.
I was literally only doing that based on out of date information told to me by Christine, and the other guy.
That other guy did not know what he was talking about. Talking about how the embeddings were going to be the most important thing.
Yes. Embeddings play a role. But like. What was the point of that question? I don't get it.


# gpt model ids


Vision models
Vision capabilities appeared to be "good" in gpt4 and gpt5. Earlier gpt3 models weren't supposed to be that good for vision.
So, should test things on these models.

## gpt-5 models

- gpt-5: the best model for coding and agentic tasks
- gpt-5-nano: the fastest, most cost-efficient version of gpt-5
- gpt-5-mini: a faster, more cost-efficient version of gpt-5, for well-defined tasks.


## gpt-4 models

- gpt-4.1: smartest, non-reasoning model
- gpt-4.1-mini: smaller, faster version of gpt-4.1
- gpt-4.1-nano: fastest, most cost efficient version of gpt-4.1.


- gpt-4o: task-focused, workhose model. low cost.
- gpt-4o-mini: faster, task-focuseed, workhose model. low cost.



So the nano is *always* the fastest, most cost-efficient version of the iteration.



# Caveats for selecting gpt models

Should be aware of the following things.
- cost per token 
- max context window size
- input and output modalities
- knowledge cutoff dates.


Especially the last thing.




# Estimating token cost


Our inputs are both text and pdf images.
But Open AI API pricing does not specify image input cost for models other than gpt-realtime.
So I can estimate the text token costs, but this is an underestimate of the true cost.
- I could check my usage on the dashboard and estimate that way. I guess.




# Updates to curation instructions


- New fields 
    - hpsreg_name in basic data


- Accepted values for 
    - Culture medium passage method




New instructions 
- in cell line retrieval specify to only retrieve cell names to curate if the article reports on these cell lines being derived therein
- also mention to beware of alternative names and these should not be retrieved to curate





# Not really getting the hpscreg_names right


- Give it example hpscreg ids
- Describe the format of the id 
- What to do in case cannot find the id





Then for all the articles which were curated
- Find the true number of hpscreg lines which came from them
- Compare against the ones ai found 
- Report of percentage of lines found by the ai that were truly there






# Methods

Need to justify using temperature=1 
- Temperature=1 is the only accepted value with newer models, like gpt-5.
    This temperature value is supposed to strike a balance between consistency and generativity.
    We hypothesised that to have comparable results, we should maintain consistent temperature values.
    Therefore we chose this value in our experiments.







# Results


I think in the results I give metrics.
So for each publication I have the correct cell lines associated with the pmid.
I can give recall. How many of the correct ones it got.
Then also false identification rate. How many false identifications per article.

This gives an indication of something. Also need to give metrics per gpt model. See improvement in the gpt models.
Which model do we use?













## Cell line identification
The first results relate to identifying unique cell lines which were derived, in the experiments reported on in the articles.
Challenges 
- Articles talk about parental and other lines which aren't the cell lines of concern. Therefore, the model has to understand this.
- Articles are unstructured and can be verbose.
- Articles could report alternative names for cell lines without explicitly mentioning coresspondences.



Should see what consistent mistakes the different models make.

Should go through the logs at the end.
- And see which articles look mistakes.
- Cross-check entries for each model. 
- Check article formatting and verbosity.
- Comment on what happened.
- For each model, calculate identification recall and false identification rate.



Pipeline for comparing identification results 

- Check which articles differences in identification results existed in 
- Check the nature of the differences: missing cell lines, false identifications
- Check which journals the articles belonged to where there were different identifications
- Recommend a model to use for identification based on cost and identification time

Final results per model:
- Recall
- False identifications
- Missing identifications
- Separate results by journal : SCR vs. non-SCR
- Cost per article
- Average time as a function of journal and number of cell lines identified.


Next we can move on to comparison of curation results.




### Scr documents



### Non-scr documents


Models sometime could not get the correct identifier even though the article contained it.
- E.g. 32442534: ['H9CX3CR1-tdTomato', 'iMGL_abud', 'iMGL_abud-ReN', 'iMGL_abud-cholesterol', 'iMGL_muffat']
    None of these identifiers are the real one WAe009-A-24

This was gpt-4-mini. Shows that newer models are getting better are reading technical documents.
But there is still room for improvement.

Model sometimes identified more cell lines than was correct in certain articles
- E.g. 32442534: Identified ['WAe009-A-24', 'H9.CX3CR1-tdTomato', 'CX3CR1-tdTomato iMGLs']
    But only 'WAe009-A-24' is real.
    Non-scr article. Unstructured reporting. Verbose writing.




## Discussion

Disease names subject to variability in model responses
- This is the reason why ontologies exist
- Recommended to align the model responses against an ontology in post-processing
- This could be the reason for reduced scores. Post-alignment scores might be much higher than the study shows
- Humans themselves may not conform to ontologies when submitting metadata
- So reduced scores pre-ontology alignment do not necessarily reflect a weakness in the model.
- If an ontology alignment step can be implemented as post-processing in these pipelines then this is a boon to the approach




(Causes of reduced scores seen in certain metadata fields. Not following accepted values and using other values.)
Models do not follow the instructions precisely, even when told to do so.
- We believe in long instructions the models can sometimes forget to follow the instructions. 
- We told the model to only use accepted values when specific in the instruction sheet.
- However, several models returned valued for the metadata field genomic_modification.mutation_type which were not in the given accepted values list.
- The model also did the same in differentiation_results.method_used: did not restrict it's responses to the accepted values.
- The model therefore diverged from the instructions.

Recommendation to others that they may need to remind the model several times for instructions that are crucial and need to be followed in general.

Recommendation to perhaps send one request per metadata section. So the model only focuses on one section at a time. With predefined focused instructions for that section. The key seems to be getting the specificity of the task right. Large tasks that are complicated might not be feasible yet for the current foundation models.



Value for this module 
- Flip a switch and automatically curate a set of fields which you know with 90% confidence are accurate and high quality 
- Spend the rest of the time curating the more detail specific fields.




Dealing with variability in responses is a problem. 
- Still not clear how to best restrict model responses to certain values
- Saying "You must use accepted values, at the top of the instruction sheet, was not sufficient."
- Hypothesise that you will need to reiterate this important instruction in every section, for the specific section, so that the model knows it is an important instruction. It doens't "remember" otherwise....




Dealing with variability in kit names is a problem 
- Different human curators write the kit name with different specificities
- The model usually writes the most specific kit name
- Hard to entity match without exact knowledge equivalence between reprogramming kits.
- Recommend that curators check the model responses for kit names, and verify against the source material.




Dealing with variability in institutional HREC names across the ground truth and model responses...

- Too lazy to get them all
- Have to commenton them 
- Or get an index of all the mismatches and rescore the ones that are actual matches to get accurate scores 

Hard to control the vocabulary of the model though in this regard
Recommend that curators verify responses against source material or known HRECs.



One of the problems that we've had in this experiment was that not all of the ground truth data was of high quality.
- Several publications had not been completely curated. The model was identifying cell lines in them where there was no corresponding ground truth entry.
- The model identified 6 cell lines, but the 



## Results processing todo's
- Derivation year need to extract just the year.



