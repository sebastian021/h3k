import requests
from datetime import date

accheaders = { 'x-rapidapi-host': 'v3.football.api-sports.io', 'x-rapidapi-key': '0f91d060dda9e6880c80e07176b0809e' }



myleague_ids = {
   "WorldCup" : 1,
   "UEFAChampionsLeague" : 2,
   "UEFAEuropaLeague": 3,
   "EuroChampionship" : 4,
   "UEFANationsLeague" : 5,
   "AfricaCupNations" : 6,
   "AsianCup" : 7,
   "WorldCupWomen": 8,
   "CopaAmerica" : 9,
   "Friendlies" : 10,
   "CONMEBOLSudamericana" : 11,
   "CAFChampionsLeague" : 12,
   "ConmebolLibertadores" : 13,
   "FIFAIntercontinentalCup" : 15,
   "CONCACAFChampionsLeague" : 16,
   "AFCChampionsLeague" : 17,
   "AFCCup" : 18,
   "AfricanNationsChampionship" : 19,
   "CAFConfederationCup" : 20,
   "ConfederationsCup" : 21,
   "CONCACAFGoldCup" : 22,
   "EAFFE-1FootballChampionship" : 23,
   "AFFChampionship" : 24,
   "GulfCupNations" : 25,
   "InternationalChampionsCup" : 26,
   "OFCChampionsLeague" : 27,
   "SAFFChampionship" : 28,
   "WorldCupQualificationAfrica" : 29,
   "WorldCupQualificationAsia" : 30,
   "WorldCupQualificationCONCACAF" : 31,
   "WorldCupQualificationEurope" : 32,
   "WorldCupQualificationOceania" : 33,
   "WorldCupQualificationSouthAmerica" : 34,
   "AsianCupQualification" : 35,
   "AfricaCupNationsQualification" : 36,
   "WorldCupQualificationIntercontinentalPlay-offs" : 37,
   "PremierLeague" : 39,
   "EnglandFACup": 45,
   "EFLTrophy" : 46,
   "EnglandLeagueCup" : 48,
   "Ligue1" : 61,
   "CoupeDelaLigue" : 65,
   "CoupeDeFrance" : 66,
   "BrasilSerieA" : 71,
   "CopaDoBrasil" : 73,
   "Bundesliga" : 78,
   "DFBPokal" : 81,
   "Eredivisie" : 88,
   "NetherlandsKNVBBeker" : 90,
   "PortugalPrimeiraLiga" : 94,
   "TaçaDePortugal" : 96,
   "J1League" : 98,
   "JLeagueCup" : 101,
   "EmperorCup" : 102,
   "LigaProfesionalArgentina" : 128,
   "CopaArgentina" : 130,
   "SerieA" : 135,
   "CoppaItalia" : 137,
   "Laliga" : 140,
   "CopaDelRey" : 143,
   "TurkeySuperLig" : 203,
   "TurkeyCup" : 206,
   "MLS" : 253,
   "USOpenCup" : 257,
   "PersianGulfProLeague" : 290,
   "AzadeganLeague" : 291,
   "KLeague1" : 292,
   "KoreaFACup" : 294,
   "UAEProLeague" : 301,
   "UAELeagueCup" : 302,
   "QatarStarsLeague" : 305,
   "SaudiProLeague" : 307,
   "OlympicsMen" : 480,
   "QueenslandNPL" : 482,
   "ArgentinaCopaDelaSuperliga" : 483,
   "HazfiCup" : 495,
   "SaudiKingCup" : 504,
   "EnglandCommunityShield" : 528,
   "GermanySuperCup" : 529,
   "UEFASuperCup" : 531,
   "AFCU23AsianCup" : 532,
   "CAFSuperCup" : 533,
   "CONMEBOLRecopa" : 541,
   "NetherlandSuperCup" : 543,
   "ItalySuperCup" : 547,
   "JPSuperCup": 548,
   "PortugalSuperCup": 550,
   "TurkeySuperCup": 551,
   "SpainSuperCup": 556,
   "AsianGames": 803,
   "CaribbeanCup": 804,
   "CONCACAFNationsLeagueQualification": 808,
   "ArgentinaSuperCopa": 810,
   "SaudiSuperCup": 826,
   "UAESuperCup": 896,
   "IranSuperCup": 905,
   "UAEQatarSuperShield": 1089,
   "OlympicsIntercontinentalPlay-offs": 1105,

        }


def get_year():
    yurl = 'https://v3.football.api-sports.io/leagues'
    params = {'id': 140, 'current': 'true'}
    
    response = requests.get(yurl, headers=accheaders, params=params)
    res = response.json()
    res = res['response'][0]['seasons'][0]
    year = res['year']
    
    return year



def get_today_date():
  """Returns today's date in YYYY-MM-DD format."""
  today = date.today()
  return today.strftime("%Y-%m-%d")
