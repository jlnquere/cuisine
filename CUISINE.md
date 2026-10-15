# Cuisine

Site Quartz alimenté par le dossier `10 Workspaces/Perso/Cuisine` du vault Foundation.

## Mettre à jour

Depuis ce dossier :

```sh
npm run import:cuisine
npm run build
git add content import-report.json
git commit -m "Update recipes"
git push origin main
```

L’import lit le vault et remplace uniquement le dossier `content` de ce projet. Les fichiers du vault restent inchangés. Les images exportées sont redimensionnées, leurs originaux sont conservés dans Obsidian.

Les README d’organisation et l’index du plugin Obsidian sont remplacés par une navigation web. Les liens vers des notes hors Cuisine deviennent du texte. Un lien de fichier manquant arrête l’import et conserve l’export précédent.

Pour un autre emplacement du vault : `python3 scripts/import-cuisine.py --vault "/chemin/Foundation"`, puis `node scripts/optimize-images.mjs`.

## Aperçu local

```sh
npm run preview
```

## Publication

Le dépôt public ne contient que le site et l’export Cuisine. Chaque push sur `main` déclenche une compilation et un déploiement GitHub Pages. Les modifications du vault ne sont pas publiées automatiquement : relancer l’import et les commandes ci-dessus.

Adresse : https://jlnquere.github.io/cuisine/
