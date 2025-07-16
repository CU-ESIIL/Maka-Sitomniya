# Markdown for the Modern Researcher at ESIIL

## Introduction

- Overview of Markdown's relevance and utility in modern research.
- How Markdown streamlines documentation in diverse scientific and coding environments.

## Section 1: Mastering Markdown Syntax

- **Objective:** Equip researchers with a thorough understanding of Markdown syntax and its diverse applications.
- **Topics Covered:**
  - Fundamentals of Text Formatting (headings, lists, bold, italics)
  - Advanced Structures (tables, blockquotes)
  - Integrating Multimedia (image and video links)
  - Diagrams with Mermaid (creating flowcharts, mind maps, timelines)
  - Interactive Elements (hyperlinks, embedding interactive content)
- **Activities:**
  - Crafting a Markdown document with various formatting elements.
  - Developing diagrams using Mermaid for research presentations.
  - Embedding multimedia elements in a Markdown document for enhanced communication.

## Section 2: Markdown in Research Tools

- **Objective:** Showcase the integration of Markdown in RStudio and Jupyter Notebooks for scientific documentation.
- **Topics Covered:**
  - Implementing Markdown in RStudio (R Markdown, knitting to HTML/PDF)
  - Utilizing Markdown in Jupyter Notebooks (code and Markdown cells)
  - Best practices for documenting research code
  - Including code outputs and visualizations in documentation
- **Activities:**
  - Creating and sharing an R Markdown document with annotated research data.
  - Building a comprehensive Jupyter Notebook with integrated Markdown annotations.

## Section 3: Disseminating Research with Markdown and GitHub Pages

- **Objective:** Teach researchers how to publish and manage Markdown-based documentation as web pages.
- **Topics Covered:**
  - Setting up a GitHub repository for hosting documentation
  - Transforming Markdown files into web-friendly formats
  - Customizing web page layouts and themes
  - Advanced features using Jekyll
  - Version control and content management for documentation
- **Activities:**
  - Publishing a research project documentation on GitHub Pages.
  - Applying custom themes and layouts to enhance online documentation.

## Conclusion

- Review of Markdown's role in enhancing research efficiency and clarity.
- Encouraging the integration of Markdown into daily research activities for improved documentation and dissemination.

## Additional Resources

- Curated list of advanced Markdown tutorials, guides for GitHub Pages, and Jekyll resources for researchers.




## Section 1: Mastering Markdown Syntax

### 1. Fundamentals of Text Formatting

- **Headings**: Use `#` for different levels of headings.
  - # Heading Level 1
  - ## Heading Level 2
  - ### Heading Level 3

- **Lists**: Bulleted lists use asterisks, numbers for ordered lists.
  - Item 1
  - Item 2
    - Subitem 2.1
    - Subitem 2.2
  - 1. First item
  - 2. Second item

- **Bold and Italics**: Use asterisks or underscores.
  - **Bold Text**
  - *Italic Text*

### 2. Advanced Structures

- **Tables**: Create tables using dashes and pipes.
  - | Header 1 | Header 2 | Header 3 |
    |----------|----------|----------|
    | Row 1    | Data     | Data     |
    | Row 2    | Data     | Data     |
  - Add a ":"" to change text justification. Here the : is added on the left for left justification.
    | Header 1 | Header 2 | Header 3 |
    |---------:|--------- |----------|
    | Row 1    | Data     | Data     |
    | Row 2    | Data     | Data     |

  - |   |   |   |   |   |   |   |   |   |   |   |   |
    |---|---|---|---|---|---|---|---|---|---|---|---|
    | A | N | A | L | Y | T | I | C | S | E | N | R |
    | E | I | N | V | I | R | O | N | M | E | N | T |
    | V | E | L | O | P | M | O | C | O | M | U | N |
    | E | G | A | G | E | L | L | A | H | C | N | E |
    | R | A | T | A | D | E | V | E | L | O | P | W |
    | E | I | T | S | I | T | N | E | I | C | S | R |
    | S | O | I | G | O | L | O | I | B | H | T | L |
    | A | H | T | L | A | E | W | E | G | N | E | L |
    | T | I | T | S | I | T | N | E | I | C | S | N |
    | I | E | E | S | R | E | H | T | O | E | N | I |
    | C | S | L | L | A | H | C | E | G | L | A | N |
    | E | G | A | L | L | E | H | C | N | E | I | C |

  - If you hit the boundaries of Markdown's capabilities, you can start to add html directly. Remember, this entire exercisse is to translate to html. 

**Sudoku Puzzle**
Fill in the blank cells with numbers from 1 to 9, such that each row, column, and 3x3 subgrid contains all the numbers from 1 to 9 without repetition.

|   |   |   |   |   |   |   |   |   |
|---|---|---|---|---|---|---|---|---|
| 5 | 3 |   |   | 7 |   |   |   |   |
| 6 |   |   | 1 | 9 | 5 |   |   |   |
|   | 9 | 8 |   |   |   |   | 6 |   |
| 8 |   |   |   | 6 |   |   |   | 3 |
| 4 |   |   | 8 |   | 3 |   |   | 1 |
| 7 |   |   |   | 2 |   |   |   | 6 |
|   | 6 |   |   |   |   | 2 | 8 |   |
|   |   |   | 4 | 1 | 9 |   |   | 5 |
|   |   |   |   | 8 |   |   | 7 | 9 |




<table>
  <tr><td style="color: blue;">5</td><td style="color: blue;">3</td><td style="color: grey;">4</td><td style="color: grey;">6</td><td style="color: blue;">7</td><td style="color: grey;">8</td><td style="color: grey;">9</td><td style="color: grey;">1</td><td style="color: grey;">2</td></tr>
  <tr><td style="color: blue;">6</td><td style="color: grey;">7</td><td style="color: grey;">2</td><td style="color: blue;">1</td><td style="color: blue;">9</td><td style="color: blue;">5</td><td style="color: grey;">3</td><td style="color: grey;">4</td><td style="color: grey;">8</td></tr>
  <tr><td style="color: grey;">1</td><td style="color: blue;">9</td><td style="color: blue;">8</td><td style="color: grey;">3</td><td style="color: grey;">4</td><td style="color: grey;">2</td><td style="color: grey;">5</td><td style="color: blue;">6</td><td style="color: grey;">7</td></tr>
  <tr><td style="color: blue;">8</td><td style="color: grey;">5</td><td style="color: grey;">9</td><td style="color: grey;">7</td><td style="color: blue;">6</td><td style="color: grey;">1</td><td style="color: grey;">4</td><td style="color: grey;">2</td><td style="color: blue;">3</td></tr>
  <tr><td style="color: blue;">4</td><td style="color: grey;">2</td><td style="color: grey;">6</td><td style="color: blue;">8</td><td style="color: grey;">5</td><td style="color: blue;">3</td><td style="color: grey;">7</td><td style="color: grey;">9</td><td style="color: blue;">1</td></tr>
  <tr><td style="color: blue;">7</td><td style="color: grey;">1</td><td style="color: grey;">3</td><td style="color: grey;">9</td><td style="color: blue;">2</td><td style="color: grey;">4</td><td style="color: grey;">8</td><td style="color: grey;">5</td><td style="color: blue;">6</td></tr>
  <tr><td style="color: grey;">9</td><td style="color: blue;">6</td><td style="color: grey;">1</td><td style="color: grey;">5</td><td style="color: grey;">3</td><td style="color: grey;">7</td><td style="color: blue;">2</td><td style="color: blue;">8</td><td style="color: grey;">4</td></tr>
  <tr><td style="color: grey;">2</td><td style="color: grey;">8</td><td style="color: grey;">7</td><td style="color: blue;">4</td><td style="color: blue;">1</td><td style="color: blue;">9</td><td style="color: grey;">6</td><td style="color: grey;">3</td><td style="color: blue;">5</td></tr>
  <tr><td style="color: grey;">3</td><td style="color: grey;">4</td><td style="color: grey;">5</td><td style="color: grey;">2</td><td style="color: blue;">8</td><td style="color: grey;">6</td><td style="color: grey;">1</td><td style="color: grey;">7</td><td style="color: blue;">9</td></tr>
</table>





- **Blockquotes**: Use `>` for blockquotes.
  - > This is a blockquote.
  - > It can span multiple lines.

### 3. Integrating Multimedia

- **Images**: Add images using the format `![alt text](image_url)`.
  - ![Markdown Logo](https://example.com/markdown-logo.png)

- **Videos**: Embed videos using HTML in Markdown.
  - `<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allowfullscreen></iframe>`

### 4. Diagrams with Mermaid

- **Flowcharts**:

```mermaid
    graph TD
    A[Start] --> B[Analyze Data]
    B --> C{Is Data Large?}
    C -->|Yes| D[Apply Big Data Solutions]
    C -->|No| E[Use Traditional Methods]
    D --> F[Machine Learning]
    E --> G[Statistical Analysis]
    F --> H{Model Accurate?}
    G --> I[Report Results]
    H -->|Yes| J[Deploy Model]
    H -->|No| K[Refine Model]
    J --> L[Monitor Performance]
    K --> F
    L --> M[End: Success]
    I --> N[End: Report Generated]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style M fill:#9f9,stroke:#333,stroke-width:2px
    style N fill:#9f9,stroke:#333,stroke-width:2px
```

- **Mind Maps**:
```mermaid
    mindmap
  root((ESIIL))
    section Data Sources
      Satellite Imagery
        ::icon(fa fa-satellite)
      Remote Sensing Data
        Drones
        Aircraft
      On-ground Sensors
        Weather Stations
        IoT Devices
      Open Environmental Data
        Public Datasets
        ::icon(fa fa-database)
    section Research Focus
      Climate Change Analysis
        Ice Melt Patterns
        Sea Level Rise
      Biodiversity Monitoring
        Species Distribution
        Habitat Fragmentation
      Geospatial Analysis Techniques
        Machine Learning Models
        Predictive Analytics
    section Applications
      Conservation Strategies
        ::icon(fa fa-leaf)
      Urban Planning
        Green Spaces
      Disaster Response
        Flood Mapping
        Wildfire Tracking
    section Tools and Technologies
      GIS Software
        QGIS
        ArcGIS
      Programming Languages
        Python
        R
      Cloud Computing Platforms
        AWS
        Google Earth Engine
      Data Visualization
        D3.js
        Tableau
```

- **Timelines**:

```mermaid
gantt
    title ESIIL Year 2 Project Schedule
    dateFormat  YYYY-MM-DD
    section CI
    Sovereign OASIS via private jupiterhubs :2024-08-01, 2024-10-30
    OASIS documentation                    :2024-09-15, 70d
    Data cube OASIS via cyverse account    :2024-09-15, 100d
    Integrate with ESIIL User Management system :2024-08-01, 2024-11-30
    Build badges to deploy DE from mkdoc   :2024-09-01, 2024-12-15
    Streamline Github ssh key management   :2024-10-01, 2024-12-31
    Cyverse support (R proxy link)         :2024-11-01, 2024-12-31
    Cyverse use summary and statistics     :2024-08-01, 2024-12-15
    
    section CI Consultation and Education
    Conferences/Invited talks              :2024-08-01, 2024-12-31
    Office hours                           :2024-08-15, 2024-12-15
    Proposals                              :2024-09-01, 2024-11-15
    Private lessons                        :2024-09-15, 2024-11-30
    Pre-event trainings                    :2024-10-01, 2024-12-15
    Textbook development w/ education team :2024-08-01, 2024-12-15
    Train the trainers / group lessons     :2024-08-15, 2024-11-30
    Tribal engagement                      :2024-09-01, 2024-12-15
    Ethical Space training                 :2024-09-15, 2024-12-31
    
    section CI Design and Build
    Data library (repository)              :2024-08-01, 2024-10-30
    Analytics library (repository)         :2024-08-15, 2024-11-15
    Containers (repository)                :2024-09-01, 2024-11-30
    Cloud infrastructure templates (repository) :2024-09-15, 2024-12-15
    Tribal resilience Data Cube            :2024-10-01, 2024-12-31
```

```mermaid

%%{init: { 'logLevel': 'debug', 'theme': 'base', 'gitGraph': {'rotateCommitLabel': true}} }%%
gitGraph
  commit id: "Start from template"
  branch c1
  commit id: "Set up SSH key pair"
  commit id: "Modify _config.yml for GitHub Pages"
  commit id: "Initial website structure"
  commit id: "Add new markdown pages"
  commit id: "Update navigation tree"
  commit id: "Edit existing pages"
  commit id: "Delete old markdown pages"
  commit id: "Finalize website updates"
  commit id: "Add new markdown pages"
  commit id: "Update navigation tree"
checkout c1
   
  branch b1
  
  commit
  commit
  checkout c1
  merge b1
```

```mermaid
%%{init: {"quadrantChart": {"chartWidth": 400, "chartHeight": 400}, "themeVariables": {"quadrant1TextFill": "#ff0000"} }}%%
quadrantChart
  x-axis Urgent --> Not Urgent
  y-axis Not Important --> "Important ❤"
  quadrant-1 Plan
  quadrant-2 Do
  quadrant-3 Delegate
  quadrant-4 Delete
```


```mermaid
timeline
    title Major Events in Environmental Science and Data Science
    section Environmental Science
        19th century : Foundations in Ecology and Conservation
        1962 : Publication of 'Silent Spring' by Rachel Carson
        1970 : First Earth Day
        1987 : Brundtland Report introduces Sustainable Development
        1992 : Rio Earth Summit
        2015 : Paris Agreement on Climate Change
    section Data Science
        1960s-1970s : Development of Database Management Systems
        1980s : Emergence of Data Warehousing
        1990s : Growth of the World Wide Web and Data Mining
        2000s : Big Data and Predictive Analytics
        2010s : AI and Machine Learning Revolution
        2020s : Integration of AI in Environmental Research
```




```mermaid
erDiagram
    CAR ||--o{ NAMED-DRIVER : allows
    CAR {
        string registrationNumber
        string make
        string model
    }
    PERSON ||--o{ NAMED-DRIVER : is
    PERSON {
        string firstName
        string lastName
        int age
    }
```

```mermaid
---
config:
  sankey:
    showValues: false
---
sankey-beta

NASA Data,Big Data Harmonization,100
    Satellite Imagery,Big Data Harmonization,80
    Open Environmental Data,Big Data Harmonization,70
    Remote Sensing Data,Big Data Harmonization,90
    Big Data Harmonization, Data Analysis and Integration,340
    Data Analysis and Integration,Climate Change Research,100
    Data Analysis and Integration,Biodiversity Monitoring,80
    Data Analysis and Integration,Geospatial Mapping,60
    Data Analysis and Integration,Urban Planning,50
    Data Analysis and Integration,Disaster Response,50
```


### 5. Interactive Elements

- **Hyperlinks**: Use the format `[link text](URL)`.
  - [Google](https://www.google.com)
  - [Play Tetris](https://tetris.com/play-tetris)

- **Embedding Interactive Content**: Use HTML tags or specific platform embed codes.
  - `<iframe src="https://example.com/interactive-content" width="600" height="400"></iframe>`




### 6. Math Notation

Markdown can be combined with LaTeX for mathematical notation, useful in environmental data science for expressing statistical distributions, coordinate systems, and more. This requires a Markdown renderer with LaTeX support (like MathJax or KaTeX).

- **Inline Math**: Use single dollar signs for inline math expressions. Representing the normal distribution.

  Example: The probability density function of the normal distribution is given by $f(x|\mu,\sigma) = \frac{1}{\sigma\sqrt{2\pi}}e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$.`

- **Display Math**: Use double dollar signs for standalone equations.

  Example:
  $$
  f(x|\mu,\sigma) = \frac{1}{\sigma\sqrt{2\pi}}e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}
  $$
  

- **Common LaTeX Elements for Environmental Data Science**:
  - **Statistical Distributions**:
    - Normal Distribution: `\frac{1}{\sigma\sqrt{2\pi}}e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}` for $\frac{1}{\sigma\sqrt{2\pi}}e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$
    - Poisson Distribution: `P(k; \lambda) = \frac{\lambda^k e^{-\lambda}}{k!}` for $P(k; \lambda) = \frac{\lambda^k e^{-\lambda}}{k!}$
  - **Coordinate Systems**:
    - Spherical Coordinates: `(r, \theta, \phi)` for $(r, \theta, \phi)$
    - Cartesian Coordinates: `(x, y, z)` for $(x, y, z)$
  - **Geospatial Equations**:
    - Haversine Formula for Distance: `a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)` for $a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$

Note: The rendering of these equations as formatted math will depend on your Markdown viewer's LaTeX capabilities.



### 7. Effective Citations in Markdown

## Inline Citations

- **Objective:** Learn how to use inline citations in Markdown.
- **Example Usage:**
  - Inline citation of a single work: 
    - Some text with an inline citation. [@jones:envstudy:2020]
  - Inline citation with specific page or section: 
    - More text with a specific section cited. [See @jones:envstudy:2020, §4.2]
  - Contrasting views: 
    - Discussion of a topic with a contrasting view. [Contra @smith:climatechange:2019, p. 78]

## Footnote Citations

- **Objective:** Understand how to use footnote citations in Markdown.
- **Example Usage:**
  - Citing with a footnote: 
    - Some statement in the text.[^1]
  - Multiple references to the same footnote: 
    - Another statement referring to the same source.[^1]
  - A different citation: 
    - Additional comment with a new citation.[^2]

## Creating Footnotes

- **Example Syntax:**
  - [^1]: First reference details. Example: Emma Jones, "Environmental Study," Nature Journal, May 2020, https://nature-journal.com/envstudy2020.
  - [^2]: Second reference details. Example: David Smith, "Climate Change Controversies," Science Daily, August 2019, https://sciencedaily.com/climatechange2019.


