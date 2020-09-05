<h1>Table of Contents<span class="tocSkip"></span></h1>
<div class="toc"><ul class="toc-item"><li><span><a href="#Location,-Location,-Location!" data-toc-modified-id="Location,-Location,-Location!-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Location, Location, Location!</a></span></li><li><span><a href="#Linear-Regression-on-Housing-Data" data-toc-modified-id="Linear-Regression-on-Housing-Data-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Linear Regression on Housing Data</a></span><ul class="toc-item"><li><span><a href="#This-repository-contains" data-toc-modified-id="This-repository-contains-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>This repository contains</a></span></li><li><span><a href="#Questions" data-toc-modified-id="Questions-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>Questions</a></span></li><li><span><a href="#Column-Names-and-Descriptions" data-toc-modified-id="Column-Names-and-Descriptions-2.3"><span class="toc-item-num">2.3&nbsp;&nbsp;</span>Column Names and Descriptions</a></span></li><li><span><a href="#Using-the-OSEMN-Process" data-toc-modified-id="Using-the-OSEMN-Process-2.4"><span class="toc-item-num">2.4&nbsp;&nbsp;</span>Using the OSEMN Process</a></span></li><li><span><a href="#Results" data-toc-modified-id="Results-2.5"><span class="toc-item-num">2.5&nbsp;&nbsp;</span>Results</a></span></li><li><span><a href="#Recommendations" data-toc-modified-id="Recommendations-2.6"><span class="toc-item-num">2.6&nbsp;&nbsp;</span>Recommendations</a></span></li><li><span><a href="#Next-Steps" data-toc-modified-id="Next-Steps-2.7"><span class="toc-item-num">2.7&nbsp;&nbsp;</span>Next Steps</a></span><ul class="toc-item"><li><span><a href="#Repository-Structure" data-toc-modified-id="Repository-Structure-2.7.1"><span class="toc-item-num">2.7.1&nbsp;&nbsp;</span>Repository Structure</a></span></li></ul></li></ul></li></ul></div>


# Location, Location, Location!
<br></br>
![output_132_1.png](/img/output_132_1.png)
<br></br>
# Linear Regression on Housing Data

**Author**: <a href="https://sites.google.com/skelouse.com/home/">Sam Stoltenberg</a>

## This repository contains
 -  A Jupyter notebook <a href="https://github.com/skelouse/mod-2-project/blob/master/student.ipynb">`student.ipynb`</a> showing our analysis of the King's county housing dataset.
- The dataset itself
- An interactive <a href="https://github.com/skelouse/mod-2-project/blob/master/map.html">`map.html`</a> map of King's county
- A module <a href="https://github.com/skelouse/mod-2-project/tree/master/mltools">`mltools`</a> that we built for this project for use in Linear Regression.
- A PowerPoint <a href="https://github.com/skelouse/mod-2-project/blob/master/presentation.pdf">presentation</a> of the data
- Two more Jupyter notebooks that we made in originally learning and attempting to conquer the data <a href="https://github.com/skelouse/mod-2-project/blob/master/student_old_1.ipynb">`student_old_1.ipynb`</a> and <a href="https://github.com/skelouse/mod-2-project/blob/master/student_old_2.ipynb">`student_old_2.ipynb`</a>



## Questions

 - What should you change about your home to increase its value?
- How many rooms should you add, should it be a bedroom or bathroom?
- How many square feet should you add, and in what form?
- The condition or overall grade of the home?


## Column Names and Descriptions
 * **id** - unique identified for a house
* **dateDate** - house was sold
* **pricePrice** -  is prediction target
* **bedroomsNumber** -  of Bedrooms/House
* **bathroomsNumber** -  of bathrooms/bedrooms
* **sqft_livingsquare** -  footage of the home
* **sqft_lotsquare** -  footage of the lot
* **floorsTotal** -  floors (levels) in house
* **waterfront** - House which has a view to a waterfront
* **view** - Has been viewed
* **condition** - How good the condition is ( Overall )
* **grade** - overall grade given to the housing unit, based on King County grading system
* **sqft_above** - square footage of house apart from basement
* **sqft_basement** - square footage of the basement
* **yr_built** - Built Year
* **yr_renovated** - Year when house was renovated
* **zipcode** - zip
* **lat** - Latitude coordinate
* **long** - Longitude coordinate
* **sqft_living15** - The square footage of interior housing living space for the nearest 15 neighbors
* **sqft_lot15** - The square footage of the land lots of the nearest 15 neighbors
## Using the OSEMN Process
 - Obtain the data
- Scrub the data
- Explore the data
- Model the data
- Interpret the data
- <a href="https://machinelearningmastery.com/how-to-work-through-a-problem-like-a-data-scientist/">Reference</a>


## Results

![output_120_0.png](/img/output_120_0.png)
<div class="shadow alert alert-success">
  <strong>From the Plot:</strong> 
    <ul>
        <li>As grade increases, so does sale price.</li>
        <li>There is a strong linear relationship between <b>grade</b> and <b>price</b>.</li>
    </ul>
</div>


![output_123_0.png](/img/output_123_0.png)
<div class="shadow alert alert-success">
  <strong>From the Plot:</strong> 
    <ul>
        <li>98039 has a mean in the millions</li>
        <li>98122 has a mean just over 500,000\$</li>
        <li>This is the top 20 zipcodes from the dataset</li></ul>
</div>


## Recommendations

 - Adding square feet, a bedroom, or bathroom could increase your home value.
- Depending on water, sewage piping and location, you should add a bathroom for the
greater value increase.
- Square feet added in any form should increase the value.
- Focus on the overall grade of your home, and of your neighbors to increase the value.


## Next Steps

 - Study more features, garage, roof style, etc.
- Compare our model of King’s county to other counties.



For any additional questions, please contact <a href="mailto:sam@skelouse.com">Sam Stoltenberg</a>)


### Repository Structure

```
|   blog.ipynb
|   column_names.md
|   CONTRIBUTING.md
|   kc_house_data.csv
|   LICENSE.md
|   map.html
|   mod2_project_rubric.pdf
|   presentation.pdf
|   README.md
|   student.ipynb
|   student_old_1.ipynb
|   student_old_2.ipynb
|       
|       
+---mltools
|   |   load_then_test.py
|   |   mlframe.py
|   |   requirements.txt
|   |   test.py
|   |   __init__.py
|   |
|   |
|   +---tests...
|
|
\---styles
        custom.css

```

<a href=#Table-of-Contents>Return to top</a>
