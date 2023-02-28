# Limitations #
SLYR will always follow the development in **ESRI** and **QGIS** to provide conversion opportunities as they arise, but if non-compatibility exists, then  conversions are limited. But don't be disheartened, if the ability is in ESRI, we can always develop it within QGIS. The other way around though - well that is out of our hands, and workarounds may be attempted. 

To be transparent, we have listed the current limitations that we know of, what we are doing about it and if there is a workaround in the meantime. 
>If you know a limitation that isn't listed, please [email us](slyr@north-road.com) and we will investigate it. 
## Rule-Based Classification Symbology ##
One of our favourites features of **QGIS** Symbology is the ability to create efficient cartography through the use of Rule-Based classifications. There is currently no direct equivalent in ArcGIS Pro. Therefore, if your **QGIS** project has many layers based on rule-based classifications, try this for a workaround. 
> Painful - yes, Inefficient - yes - but let's manually capture the rule-based classification in the layer's  field. 
1. In **QGIS**, open up a layer's `attribute table`.
2. Create the number of fields required to record each rule-based classification against the features.
3. Select the fields according to your filter used in the rule-based classification.
4. Populate the fields with the name of your rule-based classification.
5. Save your edits.
6. In the `layer panel`, duplicate the layer and name it according to the rule-based classification.
7. Apply the symbology to each layers as per the rule-based classification.

> Proposed solution: still looking for one.

# Urgent fixes #
If you have a large project impacted by limitations that requires an urgent fix, contact us here at [North Road](slyr@north-road.com) and we could look at a number of options. 
- Undertake the conversion for you. This may attract a small fee, dependent on the work, but please ask. 
- You could fund the development of the solution to go into the tool for all and become a member of our [Hall of Fame](/user_guide/hall_of_fame)
>By asking us, you are letting us know of the limitation and by delivering a solution for you, it may help develop a solution for all in the tool. 
