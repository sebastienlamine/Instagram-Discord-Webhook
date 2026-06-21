# Instagram → Discord Notifier

Envoie automatiquement une notification dans un salon Discord à chaque nouveau post d'un compte Instagram public.

**Fonctionne 100% en ligne — pas besoin d'un PC allumé, pas de compte Instagram requis, gratuit.**

---

## Comment ça marche

1. cron-job.org déclenche le workflow GitHub Actions toutes les 30 minutes
2. Le script interroge Apify qui scrape le compte Instagram cible
3. Si un nouveau post est détecté → une notification est envoyée dans ton salon Discord
4. L'ID du dernier post vu est sauvegardé pour éviter les doublons

---

## Prérequis

- Un compte [GitHub](https://github.com) (gratuit)
- Un compte [Apify](https://apify.com) (gratuit — $5 de crédits/mois offerts)
- Un compte [cron-job.org](https://cron-job.org) (gratuit)
- Un serveur Discord avec droits d'administration
- Un webhook Discord créé dans le salon où tu veux recevoir les notifications (expliqué à l'étape 2)

---

## Installation étape par étape

### Étape 1 — Copier le projet

1. Va sur [https://github.com/bionixium/Instagram-Discord-Webhook](https://github.com/bionixium/Instagram-Discord-Webhook)
2. Clique sur le bouton **Fork** en haut à droite
3. Clique sur **Create fork**

Tu as maintenant ta propre copie du projet sur ton compte GitHub.

---

### Étape 2 — Créer le webhook Discord

1. Ouvre ton serveur Discord
2. Fais un clic droit sur le salon où tu veux recevoir les notifications
3. **Paramètres du salon** → **Intégrations** → **Webhooks** → **Nouveau webhook**
4. Donne-lui un nom (ex: `Instagram Bot`)
5. Clique **Copier l'URL du webhook**
6. Garde cette URL de côté

---

### Étape 3 — Créer un compte Apify et récupérer le token

1. Crée un compte gratuit sur [apify.com](https://apify.com)
2. Clique sur ton **icône de profil** en haut à droite → **Settings**
3. Dans le menu de gauche → **API & Integrations**
4. Copie ton **Personal API token**

> Le plan gratuit offre $5 de crédits par mois. À 30 minutes d'intervalle, le bot consomme environ $3.89/mois — tu restes dans les limites gratuites.

---

### Étape 4 — Configurer les secrets GitHub

Dans ton repo forké sur GitHub :

1. Va dans **Settings** → **Secrets and variables** → **Actions**
2. Clique sur **New repository secret** et ajoute ces 3 secrets :

| Nom du secret | Valeur |
|---|---|
| `APIFY_TOKEN` | Ton token Apify |
| `IG_TARGET` | Username Instagram à surveiller (ex: `lebronjames`) |
| `WEBHOOK_URL` | URL du webhook Discord |

> ⚠️ Le username Instagram c'est ce qui apparaît dans l'URL du profil : `instagram.com/lebronjames` → username = `lebronjames`

---

### Étape 5 — Activer GitHub Actions

1. Dans ton repo, clique sur l'onglet **Actions**
2. Si GitHub te demande d'activer les workflows, clique **I understand my workflows, go ahead and enable them**

---

### Étape 6 — Créer un token GitHub pour cron-job.org

1. GitHub → icône profil → **Settings**
2. Menu gauche tout en bas → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)**
5. Donne-lui un nom (ex: `cron-job`)
6. Coche uniquement **`workflow`**
7. Expiration → **No expiration**
8. Clique **Generate token** et copie-le

---

### Étape 7 — Configurer cron-job.org

1. Crée un compte gratuit sur [cron-job.org](https://cron-job.org)
2. Clique **CREATE CRONJOB**
3. Remplis les champs :
   - **Title** : `Instagram Monitor`
   - **URL** : `https://api.github.com/repos/TON_USERNAME/Instagram-Discord-Webhook/actions/workflows/monitor.yml/dispatches`
   - **Schedule** : Every 30 minutes
4. Clique sur **ADVANCED** puis :
   - **Request method** : `POST`
   - **Request headers** → ajoute ces 2 headers :
     - `Authorization` → `Bearer TON_TOKEN_GITHUB`
     - `Accept` → `application/vnd.github+json`
   - **Request body** : `{"ref":"main"}`
5. Clique **CREATE**

> Remplace `TON_USERNAME` par ton nom d'utilisateur GitHub dans l'URL.

---

### Étape 8 — Premier lancement

1. Dans cron-job.org, ouvre ton cronjob et clique sur le bouton **Test** pour le lancer manuellement
2. Va dans l'onglet **Actions** de ton repo GitHub
3. Un run doit apparaître — clique dessus pour voir les logs

Tu dois voir dans les logs :
```
Checking @username via Apify …
Latest post ID: xxxxxxxxxx
First run — state recorded, nothing sent to Discord.
```

C'est normal — au premier lancement rien n'est envoyé sur Discord. À partir du prochain post de la personne surveillée, tu recevras automatiquement une notification.

---

## Vérifier que tout fonctionne

- Onglet **Actions** → le job doit être **vert** ✅
- Si le job est **rouge** ❌ → clique dessus et regarde l'étape qui a échoué

### Erreurs fréquentes

| Erreur | Solution |
|---|---|
| `Missing environment variables` | Un secret GitHub est manquant ou mal orthographié |
| `Apify error 401` | Token Apify invalide ou expiré |
| `No posts returned` | Le compte Instagram est privé ou n'existe pas |
| `Discord webhook error 404` | L'URL du webhook Discord est invalide |

---

## Changer l'intervalle de vérification

L'intervalle se configure dans cron-job.org (pas dans le code).

| Intervalle | Coût Apify/mois |
|---|---|
| 15 minutes | ~$5.83 ⚠️ |
| 30 minutes | ~$3.89 ✅ |
| 1 heure | ~$1.94 ✅ |

> Ne pas descendre sous 30 minutes pour rester dans le plan gratuit Apify.

---

## Structure du projet

```
├── instagram-discord.py        # Script principal
├── requirements.txt            # Dépendances Python
├── state.txt                   # ID du dernier post vu (créé automatiquement)
└── .github/
    └── workflows/
        └── monitor.yml         # Configuration GitHub Actions
```

---

## Personnalisation du message Discord

Toutes les modifications se font dans le fichier `instagram-discord.py`, dans la fonction `send_to_discord`.

---

### Changer le titre du message

Trouve cette ligne :
```python
"title": f"Nouveau post de @{IG_TARGET} ! Va vite le voir !",
```
Remplace le texte entre guillemets par ce que tu veux. Le `{IG_TARGET}` sera remplacé automatiquement par le username Instagram.

---

### Changer la couleur de la barre latérale

Trouve cette ligne :
```python
"color": 15467852,
```
Remplace `15467852` par le code décimal de ta couleur. Pour convertir une couleur :
1. Choisis ta couleur sur [htmlcolorcodes.com](https://htmlcolorcodes.com)
2. Copie le code hexadécimal (ex: `#FF5733`)
3. Convertis-le sur [binaryhexconverter.com](https://www.binaryhexconverter.com/hex-to-decimal-converter) (ex: `FF5733` → `16734003`)
4. Remplace le nombre dans le code

---

### Activer ou désactiver le @everyone

**Pour désactiver le @everyone**, remplace :
```python
"content": "@everyone",
"allowed_mentions": {"parse": ["everyone"]},
```
par :
```python
"content": "",
```

**Pour mentionner un rôle spécifique** à la place de @everyone :
```python
"content": "<@&ID_DU_ROLE>",
```
> Pour obtenir l'ID d'un rôle Discord : active le mode développeur dans Discord (Paramètres → Avancé → Mode développeur), puis fais clic droit sur le rôle → **Copier l'identifiant**.

---

### Après chaque modification

```bash
git add .
git commit -m "feat: personnalisation du message Discord"
git pull --rebase
git push
```

Puis vide `state.txt` sur GitHub et teste via cron-job.org pour voir le résultat.

---

## Crédits

- Projet original par [Fernando](https://github.com/fernandod1)
- Mis à jour pour 2026 par [bionixium](https://github.com/bionixium)
- Scraping via [Apify](https://apify.com)
- Scheduling via [cron-job.org](https://cron-job.org)
