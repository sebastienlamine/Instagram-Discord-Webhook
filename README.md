# Instagram → Discord Notifier

Envoie automatiquement une notification dans un salon Discord à chaque nouveau post d'un compte Instagram public.

**Fonctionne 100% en ligne — pas besoin d'un PC allumé, pas de compte Instagram requis, gratuit.**

---

## Comment ça marche

1. GitHub Actions déclenche le script toutes les 30 minutes
2. Le script interroge Apify qui scrape le compte Instagram cible
3. Si un nouveau post est détecté → une notification est envoyée dans ton salon Discord
4. L'ID du dernier post vu est sauvegardé pour éviter les doublons

---

## Prérequis

- Un compte [GitHub](https://github.com) (gratuit)
- Un compte [Apify](https://apify.com) (gratuit — $5 de crédits/mois offerts)
- Un serveur Discord avec droits d'administration

---

## Installation étape par étape

### Étape 1 — Copier le projet

1. Va sur [https://github.com/sebastienlamine/Instagram-Discord-Webhook](https://github.com/sebastienlamine/Instagram-Discord-Webhook)
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

### Étape 6 — Premier lancement

1. Dans l'onglet **Actions**, clique sur **Instagram Monitor** dans la liste à gauche
2. Clique sur **Run workflow** → **Run workflow** (bouton vert)
3. Attends ~30 secondes puis clique sur le run pour voir les logs

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

Par défaut : toutes les **30 minutes**.

Pour modifier, édite le fichier `.github/workflows/monitor.yml` ligne 5 :

| Intervalle | Valeur cron | Coût Apify/mois |
|---|---|---|
| 15 minutes | `*/15 * * * *` | ~$5.83 ⚠️ |
| 30 minutes | `*/30 * * * *` | ~$3.89 ✅ |
| 1 heure | `0 * * * *` | ~$1.94 ✅ |

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

## Crédits

- Projet original par [Fernando](https://github.com/fernandod1)
- Mis à jour pour 2026 par [sebastienlamine](https://github.com/sebastienlamine)
- Scraping via [Apify](https://apify.com)
