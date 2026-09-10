**Source of truth** : https://git.gregoiremureau.com/openclassroom-ai/oc-p02-paris-trees

```bash
git clone https://git.gregoiremureau.com/openclassroom-ai/oc-p02-paris-trees.git
git clone https://git.gregoiremureau.com/openclassroom-ai/oc-p02-paris-trees.git
```

Dataset: see `fetch-data.sh` (out of git if large).

# Paris Trees Analysis Project

📘 Ce projet est également disponible en [français 🇫🇷](./README.fr.md)

## 📋 Project Context

This project was carried out as part of a data analysis assignment for the **City of Paris**. The objective is to explore and analyze Paris' tree heritage from a public dataset listing the trees present across the territory of the capital.

The project focuses on the fundamentals of data science: data cleaning, anomaly handling, exploratory analysis, and statistical visualization to prepare the dataset for further analysis or business applications (urban management, biodiversity, planning).

## 🎯 Objectives

The main objectives of the project are:

1. **Explore the dataset**: Understand the structure, variable types, and characteristics of Paris' trees
2. **Clean the data**: Identify and handle missing, aberrant, and inconsistent values
3. **Analyze distributions**: Perform univariate and bivariate analyses to understand the variables
4. **Visualize the data**: Create charts and interactive maps to facilitate understanding
5. **Prepare the data**: Provide a clean and usable dataset for future analyses

## 📊 Data

The data comes from the **City of Paris Open Data** platform and contains detailed information about the trees:
- Geographic location (GPS coordinates, district, address)
- Botanical characteristics (genus, species, variety)
- Dimensions (height, circumference)
- Status (remarkable tree, ownership)
- Planting date

The dataset is included in the project under the name `p2-trees-fr.csv`.

**Source**: [Open Data City of Paris - Trees](https://opendata.paris.fr/explore/dataset/les-arbres/)

## 📁 Project Structure

```
├── Paris_trees_analysis.ipynb
├── soutenance_projet2.pptx
├── data_analysis_functions.py
├── map_arrondissement.html
├── map_lieu.html
└── p2-trees-fr.csv
```

### 1. `Paris_trees_analysis.ipynb`

**Main Notebook for Paris Trees Analysis**

This notebook is the core of the project and covers the entire exploratory analysis process:

**Data loading and overview**:
- Import of the CSV file containing the tree data
- Display of the first rows for a quick understanding
- Inspection of the DataFrame structure (types, dimensions)

**Initial exploratory analysis**:
- Use of pandas methods (`info()`, `head()`, `describe()`, `value_counts()`)
- Identification of the dataset size
- Analysis of column types and missing values
- Descriptive statistics for numerical variables

**Identification and cleaning of anomalies**:
- **Outliers**:
  - Detection for tree circumference and height
  - Use of statistical methods (IQR, z-score)
  - Correction or replacement of extreme values with `NaN`
- **Missing values**:
  - In-depth analysis of columns with NaN
  - Smart imputation for certain variables (`domanialite`, `libelle_francais`)
  - Use of correlated columns (`genre`, `espece`, `variete`) for imputation

**Univariate analysis**:
- **Quantitative variables**: distribution of height, circumference, planting year
- **Categorical variables**: breakdown by genus, species, district, remarkable status
- Visualizations: histograms, boxplots, pie charts, barplots

**Bivariate analysis**:
- Relationships between the `remarquable` status and quantitative variables (`hauteur_m`, `circonference_cm`)
- Relationships between `remarquable` and categorical variables (`espece`, `genre`)
- Correlations between numerical variables
- Statistical tests to validate observations

**Geographic analysis**:
- Distribution of trees by district
- Interactive mapping of Paris trees
- Identification of areas with high tree density

**Export of cleaned data**:
- Saving the prepared DataFrame for further analyses

### 2. `soutenance_projet2.pptx`

**Final Presentation**

This presentation summarizes:
- The context and objectives of the project
- The exploration and data cleaning methodology
- The main findings about Paris' tree heritage
- Key statistical analyses and visualizations
- Business insights (remarkable trees, distribution by district, dominant species)
- Recommendations for managing the tree heritage
- Perspectives for improvement and exploitation of the data

### 3. `data_analysis_functions.py`

**Analysis Utility Functions Module**

This Python module contains reusable functions for:
- Data cleaning (duplicate removal, NaN handling)
- Outlier identification (IQR, z-score, percentile methods)
- Outlier treatment (replacement, removal, capping)
- Variable transformation (normalization, encoding)
- Generation of data quality reports
- Standardized visualization functions

These functions were developed to be reusable on other data analysis projects.

### 4. `map_arrondissement.html`

**Interactive Map of Trees by District**

HTML file containing an interactive map (likely Folium or Plotly) that visualizes:
- The distribution of trees by Paris district
- Aggregated statistics by geographic area
- Interactive visualizations allowing zooming and exploring the data
- Potentially indicators on tree density, dominant species by district

### 5. `map_lieu.html`

**Interactive Map of Trees by Location**

HTML file containing a detailed interactive map that presents:
- The precise location of individual trees across the Paris territory
- Interactive markers with detailed information (species, height, circumference)
- Filters to explore trees by characteristics
- Clusters to improve readability in high-density areas

### 6. `p2-trees-fr.csv`

**Paris Trees Dataset**

CSV file containing raw or lightly preprocessed data on Paris trees, including:
- Identifiers and references
- Location (GPS coordinates, district, address)
- Botanical characteristics (genus, species, variety, French name)
- Dimensions (height in meters, circumference in cm)
- Status (remarkable or not, ownership)
- Planting date

## 🛠️ Technologies Used

- **Python**: Main language for data analysis
  - pandas, numpy: data manipulation and analysis
  - matplotlib, seaborn: data visualization
  - folium or plotly: interactive mapping
  - scipy: statistical tests
  - scikit-learn: outlier detection
- **Jupyter Notebook**: development and documentation
- **HTML/JavaScript**: interactive maps

## 📈 Methodology

1. **Initial exploration**: Understanding the structure and content of the dataset
2. **Cleaning**: Identification and handling of missing and aberrant values
3. **Univariate analyses**: Study of the distribution of each variable
4. **Bivariate analyses**: Exploration of relationships between variables
5. **Geographic visualization**: Interactive mapping of trees
6. **Documentation**: Presentation of results and insights

## 🎯 Expected Results

- ✅ In-depth understanding of Paris' tree heritage
- ✅ Cleaned dataset ready for advanced analyses
- ✅ Identification of remarkable trees and their characteristics
- ✅ Insights into the geographic distribution of trees
- ✅ Interactive maps to visually explore the data
- ✅ Reusable Python module for similar analyses

## 💡 Key Points of the Project

### Data Quality
Like any real-world dataset, this dataset presents challenges:
- **Missing values**: some incomplete botanical characteristics
- **Outliers**: data entry errors in measurements (impossible heights and circumferences)
- **Inconsistencies**: variations in formats and naming

### Remarkable Trees
Special attention was given to remarkable trees:
- Characteristics differentiating remarkable trees from others
- Relationships between dimensions (height, circumference) and remarkable status
- Geographic distribution of remarkable trees

### Geographic Analysis
The project integrates an important spatial dimension:
- Distribution of trees by district
- Identification of areas with high tree density
- Interactive maps for intuitive exploration
- Possibility of identifying geographic patterns

### Urban Biodiversity
The analyses reveal information about biodiversity:
- Most frequent tree species in Paris
- Botanical diversity by district
- Average age of trees (via planting dates)

## 🎓 Skills Developed

- Loading and exploring tabular data
- Cleaning real-world data with anomalies
- Handling missing values with imputation strategies
- Detection and treatment of outliers
- Univariate and bivariate statistical analyses
- Data visualization (charts and maps)
- Development of reusable Python functions
- Communication of data analysis results

## 👤 Author

**Grégoire Mureau**

---

*This project illustrates the fundamentals of exploratory data analysis: exploration, cleaning, visualization, and communication of insights, applied to a real case of urban open data.*
