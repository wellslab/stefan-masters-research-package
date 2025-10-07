


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


