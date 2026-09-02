# Residual Risk 3D Surface

Two Python scripts that turn a risk matrix into a 3D surface of the residual risk

```
Rr = ROUNDUP(Ri / C, 0)
```

where `Ri` is the initial risk and `C` the control index.

The colours are not hard coded: they are read directly from the Excel workbook, including
the conditional formatting rules of the residual risk column and the theme colours stored
in `xl/theme/`. Changing the thresholds in Excel changes the figure, with no code edit.

![Static surfaces](figures/static_surfaces.png)


## What it does

* Reads the `(Ri, C)` pairs from a worksheet and recomputes `Rr` for every pair.
* Extracts the conditional formatting rules (`lessThan`, `greaterThan`, `between`) and
  resolves their fill colours, theme references included.
* Colours each facet of the surface with the worst of its four corners, so a cell never
  looks safer than it is.
* Draws the same data twice: once with the true numeric scale of `Ri`, once with evenly
  spaced steps, because the real scale is irregular and compresses the low values.
* Produces either a PNG (Matplotlib) or a standalone interactive HTML file (Plotly) that
  works offline, with rotation, zoom, hover values and a clickable legend.

Interactive 3D Residual Hazard Modelisation : ![residual_hazard_3D](figures/residual_hazard_3d.png)

---

# Surface 3D du risque residuel

Deux scripts Python qui transforment une matrice de risques en surface 3D du risque
residuel

```
Rr = ARRONDI.SUP(Ri / C ; 0)
```

ou `Ri` est le risque initial et `C` l'indice de maitrise.

Les couleurs ne sont pas ecrites en dur : elles sont lues directement dans le classeur
Excel, a la fois les regles de mise en forme conditionnelle de la colonne du risque
residuel et les couleurs de theme stockees dans `xl/theme/`. Modifier les seuils dans
Excel modifie la figure, sans toucher au code.

![Static surfaces](figures/static_surfaces.png)

## Ce que font les scripts

* Lecture des couples `(Ri, C)` dans une feuille et recalcul de `Rr` pour chaque couple.
* Extraction des regles de mise en forme conditionnelle (`lessThan`, `greaterThan`,
  `between`) et resolution de leurs couleurs de remplissage, references de theme comprises.
* Coloration de chaque facette de la surface par le plus defavorable de ses quatre coins,
  pour qu'une case n'apparaisse jamais plus sure qu'elle ne l'est.
* Trace des memes donnees deux fois : une fois a l'echelle numerique reelle de `Ri`, une
  fois en paliers regulierement espaces, car l'echelle reelle est irreguliere et ecrase
  les faibles valeurs.
* Production soit d'un PNG (Matplotlib), soit d'un fichier HTML interactif autonome
  (Plotly) qui fonctionne hors ligne, avec rotation, zoom, valeurs au survol et legende
  cliquable.

Modélisation 3D interactive du risque résiduel : ![residual_hazard_3D](figures/residual_hazard_3d.png)
