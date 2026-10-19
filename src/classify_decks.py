"""Conservative card signatures for previously aggregated paper decklists.
Unknown is always excluded. Each recovery retains its public source and anchors.
Fetch once: python src/classify_decks.py --fetch (public Melee pages).
"""
from pathlib import Path
import csv,json,re,subprocess,hashlib
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'data/raw/classification'
def signatures(cards,raw):
 def has(*anchors):return all(a in cards for a in anchors)
 rules=[
 ('Spy Combo',['Balustrade Spy','Dread Return']),
 ('Tribe',['Tireless Tribe','Inside Out']),
 ('Familiars',['Sunscape Familiar','Snap']),
 ('Red Madness',['Fiery Temper','Guttersnipe']),
 ('Rakdos Madness',['Fiery Temper','Kitchen Imp']),
 ('Red Rally',['Rally at the Hornburg','Goblin Bushwhacker']),
 ('Red Equipment Aggro',['Goblin Tomb Raider','Inventor\'s Axe']),
 ('Burn',['Lava Spike','Skewer the Critics']),
 ('Jund Wildfire',['Cleansing Wildfire','Writhing Chrysalis','Refurbished Familiar']),
 ('Multicolor Wildfire',['Cleansing Wildfire','Baleful Strix']),
 ('Pinger Tron',['Urza\'s Tower','Mysidian Elder','Ghostly Flicker']),
 ('Flicker Tron',['Urza\'s Tower','Mnemonic Wall','Ghostly Flicker']),
 ('Monster Tron',['Urza\'s Tower','Bramble Wurm','Expedition Map']),
 ('Pactdoll Tron',['Urza\'s Tower','Pactdoll Terror']),
 ('Gardens',['Khalni Garden','Tithing Blade','Cast Down']),
 ('Sacrifice',['Carrion Feeder','Bloodthrone Vampire']),
 ('Mono Black Control',['Gray Merchant of Asphodel','Defile']),
 ('Skred',['Skred','Counterspell','Tolarian Terror']),
 ('Four Color Snow',['Skred','Baleful Strix','Abundant Growth']),
 ('Turbo Fog',["Moment's Peace",'Stream of Thought']),
 ('White Aggro',['Battle Screech',"Guardians' Pledge"]),
 ('White Weenie Affinity',['Phyrexian Walker','Salt Road Packbeast',"Martyr's Soul"]),
 ('Mardu Metalcraft',['Sneaky Snacker','Melded Moxite','Kor Skyfisher']),
 ('Synthesizer',['Experimental Synthesizer','Glint Hawk','Kor Skyfisher']),
 ('Gruul Impact Tremors',['Impact Tremors','Molten Gatekeeper','Writhing Chrysalis']),
 ('Reality Acid',['Reality Acid','Kor Skyfisher']),
 ('Azorius Allies',['Halimar Excavator','Ondu Cleric']),
 ('Pizza Combo',['Guac & Marshmallow Pizza','Banishing Knack','Steelfin Whale']),
 ('Zubera Combo',['Floating-Dream Zubera','Culling the Weak']),
 ('Golgari Altar Combo',["Ashnod's Altar",'Myr Retriever','Cauldron Familiar']),
 ('Golgari Lifegain',['Marauding Blight-Priest','Essence Warden','Blood Researcher']),
 ('Grixis Control',['Baleful Strix','Counterspell','Lightning Bolt']),
 ('Azorius Faeries',['Spellstutter Sprite','Dispatch','Kor Skyfisher']),
 ('Dimir Faeries',['Spellstutter Sprite','Baleful Strix','Cast Down']),
 ('Dimir Control',['Baleful Strix','Counterspell','Cast Down']),
 ]
 for name,anchors in rules:
  if has(*anchors):return name,anchors
 if has('Thoughtcast','Myr Enforcer') or has('Thoughtcast','Utrom Monitor'):
  if 'W-U-B-R' in raw:return 'Four Color Affinity',['Thoughtcast','Myr Enforcer']
  if 'Jeskai' in raw:return 'Jeskai Affinity',['Thoughtcast','Utrom Monitor']
  if 'Bant' in raw:return 'Bant Affinity',['Thoughtcast','Utrom Monitor']
  if 'Dimir' in raw:return 'Dimir Affinity',['Thoughtcast','Myr Enforcer']
  if 'Azorius' in raw and 'Refurbished Familiar' not in cards:return 'Azorius Affinity',['Thoughtcast','Utrom Monitor']
  if 'Dispatch' in cards and 'Galvanic Blast' in cards:return 'Four Color Affinity',['Thoughtcast','Dispatch','Galvanic Blast']
  if 'Dispatch' in cards and 'Refurbished Familiar' in cards:return 'Esper Affinity',['Thoughtcast','Dispatch','Refurbished Familiar']
  if 'Galvanic Blast' in cards and 'Reckoner\'s Bargain' in cards:return 'Grixis Affinity',['Thoughtcast','Galvanic Blast',"Reckoner's Bargain"]
  if 'W-U-B-R' in raw:return 'Four Color Affinity',['Thoughtcast','Myr Enforcer']
 return None,[]
def classify(row):
 old=row['archetype'];g=row['guid'];raw=row['raw_archetype']
 if old=='Unknown':return None,[],'excluded_unknown'
 if 'Other' not in old:return old,[],'retained_source_label'
 p=CACHE/f'{g}.html'
 if not p.exists():return None,[],'excluded_missing_decklist'
 pre=BeautifulSoup(p.read_text(),'html.parser').select_one('#decklist-text')
 if pre is None:return None,[],'excluded_unavailable_decklist'
 cards=set(re.sub(r'^\d+\s+','',line.strip()).split(' // ')[0] for line in pre.get_text().split('Sideboard')[0].splitlines())
 name,anchors=signatures(cards,raw)
 return name,anchors,'recovered_card_signature' if name else 'excluded_ambiguous'
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--fetch',action='store_true');a=p.parse_args();CACHE.mkdir(exist_ok=True)
 rows=list(csv.DictReader((ROOT/'data/processed/v2/entries.csv').open()))
 if a.fetch:
  def fetch(g):
   path=CACHE/f'{g}.html'
   if path.exists():return
   r=subprocess.run(['curl','-fLsS','--retry','2','--max-time','45',f'https://melee.gg/Decklist/View/{g}'],capture_output=True)
   if r.returncode==0:path.write_bytes(r.stdout)
  with ThreadPoolExecutor(6) as pool:list(pool.map(fetch,sorted({r['guid'] for r in rows if 'Other' in r['archetype'] and r['guid']})))
 audit=[]
 for r in rows:
  name,anchors,status=classify(r)
  audit.append(dict(**r,classified_archetype=name,status=status,anchors=anchors,source=f"https://melee.gg/Decklist/View/{r['guid']}" if r['guid'] else None, source_sha256=hashlib.sha256((CACHE/f"{r['guid']}.html").read_bytes()).hexdigest() if (CACHE/f"{r['guid']}.html").exists() else None))
 out=ROOT/'data/processed/classified';out.mkdir(exist_ok=True)
 (out/'classification_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
 from collections import Counter
 print(Counter(x['status'] for x in audit));print(Counter(x['classified_archetype'] for x in audit if 'Other' in x['archetype']))
if __name__=='__main__':main()
