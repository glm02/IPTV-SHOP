import json
import os
import random
import string
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ==== CONFIG ====
ADMIN_CHAT_ID = 6607420177
BOT_TOKEN = "7945298415:AAGD-wkM0PIKvSloh6xi6UtXTv-QeMeAV8Y"
USERS_FILE = "users.json"
ABOS_FILE = "abonnements.json"

# ==== DONNÉES CRYPTO ====
adresse_sol = "7MrWKvSE3oG3aDHQyREUYLMjMTLr36MrWR6kF1JQrrjmY"
adresse_btc = "bc1qcrvydcymsxdpntlekh3rsdf7g4ytltfmcsdhsv"
adresse_eth = "0x779Ac41100193DddC7e680AC8FF30CE078f06714"

# ==== CHARGEMENT / SAUVEGARDE DES DONNÉES ====

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_abos():
    if not os.path.exists(ABOS_FILE):
        return {"trial": [], "1m": [], "6m": [], "12m": []}
    with open(ABOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_abos():
    with open(ABOS_FILE, "w", encoding="utf-8") as f:
        json.dump(abos, f, ensure_ascii=False, indent=2)

users = load_users()
abos = load_abos()

# ==== FONCTIONS UTILITAIRES POUR LES ABONNEMENTS ====

def generer_ligne_test():
    """Génère une ligne IPTV de test aléatoire"""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return f"http://iptv.server.com/play/{code}/playlist.m3u8"

def generer_mdp_test():
    """Génère un mot de passe de test aléatoire"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def creer_abonnements_vierges():
    """Crée une base d'abonnements vierge avec des lignes de test"""
    return {
        "trial": [
            {
                "id": "trial-001",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            },
            {
                "id": "trial-002",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            },
            {
                "id": "trial-003",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            }
        ],
        "1m": [
            {
                "id": "1m-001",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            },
            {
                "id": "1m-002",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            },
            {
                "id": "1m-003",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            }
        ],
        "6m": [
            {
                "id": "6m-001",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            },
            {
                "id": "6m-002",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            }
        ],
        "12m": [
            {
                "id": "12m-001",
                "url": generer_ligne_test(),
                "mdp": generer_mdp_test(),
                "utilise": False
            }
        ]
    }

# Initialiser si le fichier n'existe pas
if not abos or not any(abos.values()):
    abos = creer_abonnements_vierges()
    save_abos()

def prendre_ligne_dispo(type_abo):
    """Prend la première ligne disponible d'un type d'abonnement"""
    if type_abo not in abos:
        return None
    
    for entree in abos[type_abo]:
        if not entree.get("utilise", False):
            entree["utilise"] = True
            save_abos()
            return entree
    
    return None

def get_stats_abos():
    """Retourne les stats des abonnements disponibles"""
    stats = {}
    for type_abo in ["trial", "1m", "6m", "12m"]:
        total = len(abos.get(type_abo, []))
        utilise = len([x for x in abos.get(type_abo, []) if x.get("utilise", False)])
        dispo = total - utilise
        stats[type_abo] = {"total": total, "utilise": utilise, "dispo": dispo}
    return stats

# ==== CLAVIERS ====
bouton_admin = KeyboardButton("Parler à l'admin💻")
bouton_abonnement = KeyboardButton("Choix abonnement IPTV")
bouton_solde = KeyboardButton("Mon solde 💰")
bouton_aide = KeyboardButton("Aide 🆘")

clavier_principal = ReplyKeyboardMarkup(
    [[bouton_admin], [bouton_abonnement], [bouton_solde], [bouton_aide]],
    resize_keyboard=True,
    one_time_keyboard=False
)

# menu crypto
btn_btc = KeyboardButton("BTC")
btn_sol = KeyboardButton("SOL")
btn_eth = KeyboardButton("ETH")
btn_back_crypto = KeyboardButton("⬅️ Retour")

clavier_crypto = ReplyKeyboardMarkup(
    [[btn_btc, btn_sol, btn_eth],
     [btn_back_crypto]],
    resize_keyboard=True,
    one_time_keyboard=False
)

# menu solde
btn_consulter_solde = KeyboardButton("Consulter mon solde")
btn_recharger_solde = KeyboardButton("Recharger mon solde 💳")
btn_retour_solde = KeyboardButton("⬅️ Retour au menu")

clavier_solde = ReplyKeyboardMarkup(
    [[btn_consulter_solde], [btn_recharger_solde], [btn_retour_solde]],
    resize_keyboard=True,
    one_time_keyboard=False
)

# menu abonnement
btn_abo_1m = KeyboardButton("Abonnement 1 mois (10€)")
btn_abo_6m = KeyboardButton("Abonnement 6 mois (50€)")
btn_abo_12m = KeyboardButton("Abonnement 12 mois (90€)")
btn_trial = KeyboardButton("Essai 24h gratuit")
btn_retour_abo = KeyboardButton("⬅️ Retour au menu")

clavier_abonnement = ReplyKeyboardMarkup(
    [[btn_abo_1m], [btn_abo_6m], [btn_abo_12m], [btn_trial], [btn_retour_abo]],
    resize_keyboard=True,
    one_time_keyboard=False
)

# ==== 1. /start : enregistre l'utilisateur + affiche le menu ====
async def start(update, context):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    if user_id not in users:
        users[user_id] = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "solde": 0.0,
            "created_at": date_str,
            "last_seen": date_str,
            "abonnement": None,
            "id_ligne_abo": None,
            "trial_used": False,
            "trial_expire_at": None,
            "id_ligne_trial": None
        }
    else:
        users[user_id]["username"] = username
        users[user_id]["first_name"] = first_name
        users[user_id]["last_seen"] = date_str
        users[user_id].setdefault("abonnement", None)
        users[user_id].setdefault("id_ligne_abo", None)
        users[user_id].setdefault("trial_used", False)
        users[user_id].setdefault("trial_expire_at", None)
        users[user_id].setdefault("id_ligne_trial", None)

    save_users()

    await update.message.reply_text(
        "Bienvenue sur le bot IPTV by UKR.\nChoisis une option dans le clavier.",
        reply_markup=clavier_principal
    )

# ==== 2. Commandes diverses ====
async def admin_present(update, context):
    await update.message.reply_text(
        "L'admin @ukr92k n'est pas en ligne, il vous répondra sous peu."
    )

async def mini_app(update, context):
    await update.message.reply_text(
        "Voici notre mini app disponible 24/7 !\nhttps://iptv-shop-delta.vercel.app/"
    )

# ==== 3. Commande admin pour voir les utilisateurs ====
async def list_users(update, context):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if not users:
        await update.message.reply_text("Aucun utilisateur enregistré.")
        return

    lignes = []
    for user_id, data in users.items():
        username = f"@{data.get('username')}" if data.get("username") else "(pas de username)"
        nom = f"{data.get('first_name') or ''} {data.get('last_name') or ''}".strip()
        abo = data.get("abonnement")
        if abo:
            abo_txt = f"{abo.get('type')} jusqu'au {abo.get('expire_at')}"
        else:
            abo_txt = "Aucun"
        trial_used = data.get("trial_used", False)
        trial_info = data.get("trial_expire_at") if trial_used else "jamais utilisé"
        solde = data.get("solde", 0.0)
        
        lignes.append(
            f"ID: {user_id} | {username} | {nom} | Solde: {solde}€ | "
            f"Abo: {abo_txt} | Essai: {trial_info}"
        )

    texte = "📋 UTILISATEURS ENREGISTRÉS :\n\n" + "\n".join(lignes)
    await update.message.reply_text(texte)

# ==== 4. Commande admin pour voir les stats des abonnements ====
async def stats_abos(update, context):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    stats = get_stats_abos()
    
    lignes = ["📊 STATS DES ABONNEMENTS :\n"]
    for type_abo, data in stats.items():
        lignes.append(
            f"• {type_abo.upper()} : {data['dispo']}/{data['total']} disponibles "
            f"({data['utilise']} utilisés)"
        )
    
    texte = "\n".join(lignes)
    await update.message.reply_text(texte)

# ==== 5. Commande admin pour ajouter du solde ====
async def add_sold(update, context):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("Commande réservée à l'admin.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage : /add_sold <user_id> <montant>")
        return

    user_id_str, montant_str = args

    try:
        target_id = str(int(user_id_str))
        montant = float(montant_str)
    except ValueError:
        await update.message.reply_text("user_id doit être un entier, montant un nombre.")
        return

    if target_id not in users:
        await update.message.reply_text(f"Utilisateur {target_id} inconnu (pas de /start ?).")
        return

    users[target_id]["solde"] = users[target_id].get("solde", 0.0) + montant
    nouveau_solde = users[target_id]["solde"]
    save_users()

    await update.message.reply_text(
        f"✅ Solde mis à jour pour {target_id}.\n"
        f"+{montant}€ (nouveau solde : {nouveau_solde}€)."
    )

    try:
        await context.bot.send_message(
            chat_id=int(target_id),
            text=f"💰 Ton solde a été crédité de {montant}€.\nNouveau solde : {nouveau_solde}€."
        )
    except Exception:
        pass

# ==== 6. Commande admin pour recharger les abonnements ====
async def reload_abos(update, context):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    global abos
    abos = creer_abonnements_vierges()
    save_abos()

    await update.message.reply_text(
        "✅ Base d'abonnements réinitialisée avec des nouvelles lignes de test."
    )

# ==== 7. Logiciel d'achat d'abonnement via solde ====
def calculer_abo(type_abo):
    if type_abo == "1m":
        prix = 10.0
        duree = timedelta(days=30)
        label = "1 mois"
    elif type_abo == "6m":
        prix = 50.0
        duree = timedelta(days=30 * 6)
        label = "6 mois"
    elif type_abo == "12m":
        prix = 90.0
        duree = timedelta(days=30 * 12)
        label = "12 mois"
    else:
        prix = 0.0
        duree = timedelta(0)
        label = "inconnu"
    return prix, duree, label

async def traiter_achat_abonnement(user_id, type_abo, update, context):
    if user_id not in users:
        await update.message.reply_text("Je ne te trouve pas dans la base (refais /start).")
        return

    prix, duree, label = calculer_abo(type_abo)
    solde = users[user_id].get("solde", 0.0)

    if solde < prix:
        await update.message.reply_text(
            f"❌ Solde insuffisant pour l'abonnement {label} ({prix}€).\n"
            f"Tu as {solde}€, il t'en faut {prix}€.\n"
            "Recharge ton solde dans le menu solde."
        )
        return

    # Prendre une ligne IPTV disponible
    ligne = prendre_ligne_dispo(type_abo)
    if ligne is None:
        await update.message.reply_text(
            f"❌ Aucune ligne {label} disponible pour le moment.\n"
            "Contacte @ukr92k pour recharger le stock."
        )
        
        # Notif admin
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⚠️ STOCK ÉPUISÉ : Plus de lignes {label} disponibles !"
        )
        return

    # Débiter le solde
    users[user_id]["solde"] = solde - prix

    # Calculer date d'expiration
    now = datetime.now()
    expire_at = now + duree
    expire_str = expire_at.strftime("%Y-%m-%d %H:%M")

    # Enregistrer l'abonnement
    users[user_id]["abonnement"] = {
        "type": label,
        "expire_at": expire_str,
        "abo_type": type_abo
    }
    users[user_id]["id_ligne_abo"] = ligne["id"]

    save_users()

    # Message au client avec la ligne
    await update.message.reply_text(
        f"✅ PAIEMENT ACCEPTÉ !\n\n"
        f"🎟 Abonnement {label} activé jusqu'au {expire_str}\n\n"
        f"📺 Voici ta ligne IPTV :\n"
        f"🔗 URL : {ligne['url']}\n"
        f"🔐 MDP : {ligne['mdp']}\n"
        f"ID Ligne : {ligne['id']}\n\n"
        f"💰 Solde restant : {users[user_id]['solde']}€\n\n"
        f"⚠️ Garde tes identifiants précieusement !"
    )

    # Notif admin
    user = update.effective_user
    username = f"@{user.username}" if user.username else "(pas de username)"
    nom = f"{user.first_name or ''} {user.last_name or ''}".strip()

    notif_admin = (
        "🎟 NOUVEL ABONNEMENT IPTV\n\n"
        f"ID User: {user.id}\n"
        f"Username: {username}\n"
        f"Nom: {nom}\n"
        f"Abonnement: {label}\n"
        f"Expire: {expire_str}\n"
        f"Ligne ID: {ligne['id']}\n"
        f"Solde après achat: {users[user_id]['solde']}€\n"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=notif_admin
    )

# ==== 8. Gestion des essais 24h ====
async def traiter_essai_24h(user_id, update, context):
    if user_id not in users:
        await update.message.reply_text("Je ne te trouve pas dans la base (refais /start).")
        return

    trial_used = users[user_id].get("trial_used", False)

    if trial_used:
        await update.message.reply_text(
            "❌ Tu as déjà utilisé ton essai 24h.\n"
            "Si tu veux continuer, choisis un abonnement IPTV payant."
        )
        return

    # Prendre une ligne IPTV trial disponible
    ligne = prendre_ligne_dispo("trial")
    if ligne is None:
        await update.message.reply_text(
            "❌ Aucune ligne essai disponible pour le moment.\n"
            "Contacte @ukr92k pour recharger le stock."
        )
        
        # Notif admin
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="⚠️ STOCK ÉPUISÉ : Plus de lignes trial disponibles !"
        )
        return

    now = datetime.now()
    expire_at = now + timedelta(hours=24)
    expire_str = expire_at.strftime("%Y-%m-%d %H:%M")

    users[user_id]["trial_used"] = True
    users[user_id]["trial_expire_at"] = expire_str
    users[user_id]["id_ligne_trial"] = ligne["id"]

    save_users()

    # Message au client avec la ligne
    await update.message.reply_text(
        f"✅ ESSAI 24H ACTIVÉ !\n\n"
        f"Valable jusqu'au {expire_str}\n\n"
        f"📺 Voici ta ligne IPTV :\n"
        f"🔗 URL : {ligne['url']}\n"
        f"🔐 MDP : {ligne['mdp']}\n"
        f"ID Ligne : {ligne['id']}\n\n"
        f"⚠️ Garde tes identifiants précieusement !"
    )

    # Notif admin
    user = update.effective_user
    username = f"@{user.username}" if user.username else "(pas de username)"
    nom = f"{user.first_name or ''} {user.last_name or ''}".strip()

    notif_admin = (
        "🎟 NOUVEL ESSAI 24H\n\n"
        f"ID User: {user.id}\n"
        f"Username: {username}\n"
        f"Nom: {nom}\n"
        f"Expire: {expire_str}\n"
        f"Ligne ID: {ligne['id']}\n"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=notif_admin
    )

# ==== 9. Commande pour voir sa ligne IPTV (récupération) ====
async def ma_ligne(update, context):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await update.message.reply_text("Tu dois d'abord faire /start.")
        return

    abo = users[user_id].get("abonnement")
    trial = users[user_id].get("trial_used", False)
    trial_expire = users[user_id].get("trial_expire_at")

    if abo:
        id_ligne = users[user_id].get("id_ligne_abo")
        expire_at = abo.get("expire_at")
        
        # Chercher la ligne dans la base
        ligne_obj = None
        abo_type = abo.get("abo_type", "1m")
        for l in abos.get(abo_type, []):
            if l["id"] == id_ligne:
                ligne_obj = l
                break
        
        if ligne_obj:
            await update.message.reply_text(
                f"📺 TA LIGNE IPTV ABONNEMENT\n\n"
                f"Type: {abo.get('type')}\n"
                f"Expire: {expire_at}\n\n"
                f"🔗 URL : {ligne_obj['url']}\n"
                f"🔐 MDP : {ligne_obj['mdp']}\n"
                f"ID : {id_ligne}"
            )
        else:
            await update.message.reply_text("Ligne non trouvée dans la base.")
    elif trial:
        id_ligne = users[user_id].get("id_ligne_trial")
        
        # Chercher la ligne dans la base
        ligne_obj = None
        for l in abos.get("trial", []):
            if l["id"] == id_ligne:
                ligne_obj = l
                break
        
        if ligne_obj:
            await update.message.reply_text(
                f"📺 TA LIGNE IPTV ESSAI\n\n"
                f"Expire: {trial_expire}\n\n"
                f"🔗 URL : {ligne_obj['url']}\n"
                f"🔐 MDP : {ligne_obj['mdp']}\n"
                f"ID : {id_ligne}"
            )
        else:
            await update.message.reply_text("Ligne essai non trouvée dans la base.")
    else:
        await update.message.reply_text(
            "Tu n'as pas d'abonnement ou d'essai actif.\n"
            "Choisis un abonnement ou essai dans le menu."
        )

# ==== 10. Gestion des boutons texte ====
async def handle_text(update, context):
    texte = update.message.text
    user = update.effective_user
    user_id = str(user.id)

    # phrase secrète panel dev
    if texte == "arracheur92i" and user.id == ADMIN_CHAT_ID:
        await update.message.reply_text(
            "🔑 PANEL DEV ACTIVÉ\n\n"
            "Commandes dispo :\n"
            "/users - liste des users\n"
            "/add_sold <id> <montant> - créditer un user\n"
            "/stats_abos - voir les stocks\n"
            "/reload_abos - réinit. les abonnements\n"
        )
        return

    if user_id in users:
        users[user_id]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_users()

    if texte == "Parler à l'admin💻":
        await update.message.reply_text("Contact admin : @ukr92k")

    elif texte == "Choix abonnement IPTV":
        await update.message.reply_text(
            "Choisis ton abonnement IPTV (paiement par solde) :",
            reply_markup=clavier_abonnement
        )

    elif texte == "Abonnement 1 mois (10€)":
        await traiter_achat_abonnement(user_id, "1m", update, context)

    elif texte == "Abonnement 6 mois (50€)":
        await traiter_achat_abonnement(user_id, "6m", update, context)

    elif texte == "Abonnement 12 mois (90€)":
        await traiter_achat_abonnement(user_id, "12m", update, context)

    elif texte == "Essai 24h gratuit":
        await traiter_essai_24h(user_id, update, context)

    elif texte == "Mon solde 💰":
        await update.message.reply_text(
            "Menu solde :",
            reply_markup=clavier_solde
        )

    elif texte == "Consulter mon solde":
        if user_id in users:
            solde = users[user_id].get("solde", 0.0)
            await update.message.reply_text(f"💰 Ton solde actuel est de : {solde}€")
        else:
            await update.message.reply_text("Je ne te trouve pas dans la base (refais /start).")

    elif texte == "Recharger mon solde 💳":
        await update.message.reply_text(
            "Choisis la crypto pour recharger ton solde :",
            reply_markup=clavier_crypto
        )

    elif texte == "⬅️ Retour au menu":
        await update.message.reply_text(
            "Retour au menu principal.",
            reply_markup=clavier_principal
        )

    elif texte == "BTC":
        await update.message.reply_text(
            f"💳 RECHARGE PAR BTC\n\n"
            f"Adresse : {adresse_btc}\n\n"
            f"Une fois ton paiement effectué, tu peux faire /ma_ligne pour voir ta ligne IPTV\n"
            f"Ou contacte @ukr92k si le solde ne s'est pas crédité."
        )

    elif texte == "SOL":
        await update.message.reply_text(
            f"💳 RECHARGE PAR SOL\n\n"
            f"Adresse : {adresse_sol}\n\n"
            f"Une fois ton paiement effectué, tu peux faire /ma_ligne pour voir ta ligne IPTV\n"
            f"Ou contacte @ukr92k si le solde ne s'est pas crédité."
        )

    elif texte == "ETH":
        await update.message.reply_text(
            f"💳 RECHARGE PAR ETH\n\n"
            f"Adresse : {adresse_eth}\n\n"
            f"Une fois ton paiement effectué, tu peux faire /ma_ligne pour voir ta ligne IPTV\n"
            f"Ou contacte @ukr92k si le solde ne s'est pas crédité."
        )

    elif texte == "⬅️ Retour":
        await update.message.reply_text(
            "Retour au menu principal.",
            reply_markup=clavier_principal
        )

    elif texte == "Aide 🆘":
        await update.message.reply_text(
            "📞 Pour toute demande, contacte @ukr92k.\n"
            "📺 Canal principal : https://t.me/ukriptvpro\n\n"
            "💡 Commandes utiles :\n"
            "/ma_ligne - voir ta ligne IPTV"
        )

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        username = f"@{user.username}" if user.username else "(pas de username)"
        nom = f"{user.first_name or ''} {user.last_name or ''}".strip()

        notif_admin = (
            "🆘 CLICK AIDE\n\n"
            f"Date: {date_str}\n"
            f"ID: {user.id}\n"
            f"Username: {username}\n"
            f"Nom: {nom}\n"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=notif_admin
        )

    else:
        await update.message.reply_text("Utilise les boutons du clavier pour naviguer.")

# ==== 11. MAIN ====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_present))
    app.add_handler(CommandHandler("mini_app", mini_app))
    app.add_handler(CommandHandler("ma_ligne", ma_ligne))

    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(CommandHandler("add_sold", add_sold))
    app.add_handler(CommandHandler("stats_abos", stats_abos))
    app.add_handler(CommandHandler("reload_abos", reload_abos))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
