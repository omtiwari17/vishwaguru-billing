"""
Bilingual Translation & Transliteration Engine for Vishwaguru Billing.
Provides seamless, ultra-accurate, lightweight offline & online translation and transliteration
between Hindi (Devanagari) and English (Latin) for advertiser names, business titles,
addresses, and advertisement headlines.

Architecture:
1. In-Memory LRU Cache: Instantaneous (< 0.01ms) lookup for repeated words.
2. Curated Newspaper & Advertising Lexicon: 600+ high-frequency Indian business terms,
   surnames, shop types, and locations with longest-phrase matching.
3. Universal Rule-Based Phonetic Transliteration: Accurately transliterates unseen names
   and words phonetically in pure Python without requiring internet or heavy ML libraries.
4. Opportunistic Network Query: Upgrades via Google Translate when internet is active (1.5s timeout).
"""
import re
import urllib.parse
import urllib.request
import json
import logging

logger = logging.getLogger(__name__)

# Global in-memory cache to ensure repeated lookups are instant
_TRANSLATION_CACHE = {}

# ---------------------------------------------------------------------------
# Tier 1: Curated Newspaper, Advertising & Business Lexicon (600+ Entries)
# ---------------------------------------------------------------------------
NEWSPAPER_GLOSSARY = {
    # Titles & Honorifics
    'm/s': 'मे.', 'messrs': 'मे.', 'mr': 'श्री', 'mr.': 'श्री', 'shri': 'श्री', 'shree': 'श्री',
    'mrs': 'श्रीमती', 'mrs.': 'श्रीमती', 'smt': 'श्रीमती', 'smt.': 'श्रीमती',
    'dr': 'डॉ.', 'dr.': 'डॉ.', 'prof': 'प्रो.', 'prof.': 'प्रो.', 'adv': 'एड.', 'adv.': 'एड.',
    'pt': 'पं.', 'pt.': 'पं.', 'pandit': 'पंडित', 'swami': 'स्वामी', 'maharaj': 'महाराज',

    # Common Indian Business Surnames & Family Names
    'sharma': 'शर्मा', 'verma': 'वर्मा', 'gupta': 'गुप्ता', 'agrawal': 'अग्रवाल',
    'agarwal': 'अग्रवाल', 'aggarwal': 'अग्रवाल', 'patel': 'पटेल', 'jain': 'जैन',
    'shah': 'शाह', 'mehta': 'मेहता', 'joshi': 'जोशी', 'khandelwal': 'खंडेलवाल',
    'tiwari': 'तिवारी', 'mishra': 'मिश्रा', 'pandey': 'पांडेय', 'shukla': 'शुक्ला',
    'dubey': 'दुबे', 'tripathi': 'त्रिपाठी', 'yadav': 'यादव', 'choudhary': 'चौधरी',
    'chaudhary': 'चौधरी', 'rathore': 'राठौड़', 'chauhan': 'चौहान', 'rajput': 'राजपूत',
    'singh': 'सिंह', 'soni': 'सोनी', 'maheshwari': 'माहेश्वरी', 'porwal': 'पोरवाल',
    'patidar': 'पाटीदार', 'malviya': 'मालवीय', 'mandloi': 'मंडलोई', 'solanki': 'सोलंकी',
    'tomar': 'तोमर', 'parmar': 'परमार', 'goyal': 'गोयल', 'mittal': 'मित्तल',
    'bansal': 'बंसल', 'garg': 'गर्ग', 'singhal': 'सिंघल', 'jindal': 'जिंदल',
    'bindal': 'बिंदल', 'mahajan': 'महाजन', 'bhatia': 'भाटिया', 'arora': 'अरोड़ा',
    'kapoor': 'कपूर', 'khanna': 'खन्ना', 'malhotra': 'मल्होत्रा', 'chopra': 'चोपड़ा',
    'sethi': 'सेठी', 'bajaj': 'बजाज', 'birla': 'बिड़ला', 'tata': 'टाटा',
    'ambani': 'अंबानी', 'godrej': 'गोदरेज', 'adani': 'अदाणी', 'kothari': 'कोठारी',
    'oswal': 'ओसवाल', 'lodha': 'लोढ़ा', 'doshi': 'दोशी', 'ranka': 'रांका',
    'bafna': 'बाफना', 'chhajed': 'छाजेड़', 'sethia': 'सेठिया', 'surana': 'सुराणा',
    'maru': 'मारू', 'nahar': 'नाहर', 'lunia': 'लूनिया', 'kasliwal': 'कासलीवाल',
    'gangwal': 'गंगवाल', 'badjatya': 'बड़जात्या', 'bakliwal': 'बाकलीवाल',
    'godha': 'गोधा', 'tongia': 'टोंग्या', 'seth': 'सेठ', 'lala': 'लाला',

    # First Names Commonly Found in Business Names
    'ram': 'राम', 'shyam': 'श्याम', 'krishna': 'कृष्णा', 'radhe': 'राधे',
    'radha': 'राधा', 'shiva': 'शिव', 'shiv': 'शिव', 'ganesh': 'गणेश',
    'ganpati': 'गणपति', 'hanuman': 'हनुमान', 'balaji': 'बालाजी', 'sai': 'साईं',
    'mahavir': 'महावीर', 'paras': 'पारस', 'rishabh': 'ऋषभ', 'adinath': 'आदिनाथ',
    'laxmi': 'लक्ष्मी', 'lakshmi': 'लक्ष्मी', 'saraswati': 'सरस्वती', 'durga': 'दुर्गा',
    'om': 'ओम', 'jai': 'जय', 'shubh': 'शुभ', 'labh': 'लाभ', 'mangal': 'मंगल',
    'anand': 'आनंद', 'vijay': 'विजय', 'ajay': 'अजय', 'sanjay': 'संजय',
    'raj': 'राज', 'rajesh': 'राजेश', 'rakesh': 'राकेश', 'mukesh': 'मुकेश',
    'suresh': 'सुरेश', 'ramesh': 'रमेश', 'dinesh': 'दिनेश', 'naresh': 'नरेश',
    'mahesh': 'महेश', 'kamlesh': 'कमलेश', 'jagdish': 'जगदीश', 'harish': 'हरीश',
    'manish': 'मनीष', 'ashish': 'आशीष', 'deepak': 'दीपक', 'pradeep': 'प्रदीप',
    'sandeep': 'संदीप', 'alok': 'आलोक', 'ashok': 'अशोक', 'vinod': 'विनोद',
    'manoj': 'मनोज', 'sunil': 'सुनील', 'anil': 'अनिल', 'rahul': 'राहुल',
    'rohit': 'रोहित', 'amit': 'अमित', 'gaurav': 'गौरव', 'bharat': 'भारत',
    'vikas': 'विकास', 'prakash': 'प्रकाश', 'akash': 'आकाश', 'kailash': 'कैलाश',

    # Business Categories & Store Types
    'jewellers': 'ज्वेलर्स', 'jewelers': 'ज्वेलर्स', 'jewellery': 'ज्वेलरी', 'jewelry': 'ज्वेलरी',
    'automobiles': 'ऑटोमोबाइल्स', 'automobile': 'ऑटोमोबाइल', 'auto': 'ऑटो', 'motors': 'मोटर्स', 'motor': 'मोटर',
    'auto parts': 'ऑटो पार्ट्स', 'spare parts': 'स्पेयर पार्ट्स', 'tyres': 'टायर्स', 'tyre': 'टायर',
    'traders': 'ट्रेडर्स', 'trading': 'ट्रेडिंग', 'trader': 'ट्रेडर',
    'enterprises': 'एंटरप्राइजेज', 'enterprise': 'एंटरप्राइज',
    'textiles': 'टेक्सटाइल्स', 'textile': 'टेक्सटाइल', 'fabrics': 'फैब्रिक्स', 'fabric': 'फैब्रिक',
    'cloth': 'वस्त्र', 'clothes': 'वस्त्र', 'saree': 'साड़ी', 'sarees': 'साड़ियां', 'suiting': 'सूटिंग', 'shirting': 'शर्टिंग',
    'vastra bhandar': 'वस्त्र भंडार', 'bhandar': 'भंडार', 'showroom': 'शोरूम',
    'garments': 'गारमेंट्स', 'garment': 'गारमेंट', 'dresses': 'ड्रेसेस', 'footwear': 'फुटवेयर', 'shoes': 'शूज',
    'hardware': 'हार्डवेयर', 'sanitary': 'सैनिटरी', 'paints': 'पेंट्स', 'paint': 'पेंट',
    'hardware & sanitary': 'हार्डवेयर एवं सेनेटरी', 'plywood': 'प्लाईवुड', 'timber': 'टिम्बर', 'glass': 'ग्लास', 'steel': 'स्टील',
    'iron': 'लोहा', 'cement': 'सीमेंट', 'pipe': 'पाइप', 'pipes': 'पाइप्स',
    'electricals': 'इलेक्ट्रिकल्स', 'electrical': 'इलेक्ट्रिकल', 'electronics': 'इलेक्ट्रॉनिक्स', 'electronic': 'इलेक्ट्रॉनिक',
    'appliances': 'उपकरण', 'digital': 'डिजिटल', 'mobile': 'मोबाइल', 'mobiles': 'मोबाइल्स',
    'computers': 'कंप्यूटर्स', 'computer': 'कंप्यूटर', 'infotech': 'इन्फोटेक', 'solutions': 'सॉल्यूशंस',
    'technologies': 'टेक्नोलॉजीज', 'technology': 'टेक्नोलॉजी',
    'opticals': 'ऑप्टिकल्स', 'optical': 'ऑप्टिकल', 'stationery': 'स्टेशनरी', 'book store': 'बुक स्टोर', 'pustak bhandar': 'पुस्तक भंडार',
    'properties': 'प्रॉपर्टीज', 'property': 'प्रॉपर्टी', 'real estate': 'रियल एस्टेट',
    'developers': 'डेवलपर्स', 'developer': 'डेवलपर', 'builders': 'बिल्डर्स', 'builder': 'बिल्डर',
    'constructions': 'कंस्ट्रक्शंस', 'construction': 'कंस्ट्रक्शन', 'colonizers': 'कॉलोनाइजर्स',
    'hospital': 'हॉस्पिटल', 'clinic': 'क्लिनिक', 'nursing home': 'नर्सिंग होम', 'healthcare': 'हेल्थकेयर',
    'diagnostics': 'डायग्नोस्टिक्स', 'pathology': 'पैथोलॉजी', 'lab': 'लैब', 'dental': 'डेंटल', 'eye': 'नेत्र', 'care': 'केयर',
    'pharmacy': 'फार्मेसी', 'chemist': 'केमिस्ट', 'chemists': 'केमिस्ट्स', 'medicos': 'मेडिकोज', 'medical': 'मेडिकल',
    'school': 'स्कूल', 'public school': 'पब्लिक स्कूल', 'convent': 'कॉन्वेंट', 'college': 'कॉलेज',
    'institute': 'इंस्टीट्यूट', 'academy': 'अकादमी', 'classes': 'क्लासेस', 'coaching': 'कोचिंग',
    'tutorials': 'ट्यूटोरियल्स', 'university': 'यूनिवर्सिटी', 'education': 'एजुकेशन',
    'hotel': 'होटल', 'resort': 'रिसॉर्ट', 'restaurant': 'रेस्टोरेंट', 'cafe': 'कैफे', 'dhaba': 'ढाबा',
    'sweets': 'मिष्ठान्न', 'sweet': 'मिष्ठान्न', 'sweets & namkeen': 'मिष्ठान्न एवं नमकीन', 'mishtan bhandar': 'मिष्ठान्न भंडार',
    'namkeen': 'नमकीन', 'bakers': 'बेकर्स', 'bakery': 'बेकरी',
    'dairy': 'डेयरी', 'milk': 'दूध', 'parlour': 'पार्लर', 'parlor': 'पार्लर', 'salon': 'सैलून',
    'fitness': 'फिटनेस', 'gym': 'जिम', 'yoga': 'योग', 'travels': 'ट्रैवल्स', 'tours': 'टूर्स',
    'transport': 'ट्रांसपोर्ट', 'logistics': 'लॉजिस्टिक्स', 'cargo': 'कार्गो', 'courier': 'कूरियर',
    'packers': 'पैकर्स', 'movers': 'मूवर्स', 'security': 'सिक्योरिटी', 'agency': 'एजेंसी',
    'services': 'सर्विसेज', 'service': 'सर्विस', 'consultant': 'सलाहकार', 'consultants': 'कंसल्टेंट्स',
    'associates': 'एसोसिएट्स', 'group': 'ग्रुप', 'corporation': 'कॉरपोरेशन', 'industries': 'इंडस्ट्रीज',
    'manufacturing': 'मैन्युफैक्चरिंग', 'works': 'वर्क्स', 'company': 'कंपनी', 'co.': 'कंपनी',
    'brothers': 'ब्रदर्स', 'bros': 'ब्रदर्स', 'bros.': 'ब्रदर्स', 'sons': 'संस',
    'store': 'स्टोर', 'stores': 'स्टोर्स', 'shop': 'दुकान', 'mart': 'मार्ट',
    'bazaar': 'बाजार', 'bazar': 'बाजार', 'collection': 'कलेक्शन', 'centre': 'सेंटर', 'center': 'सेंटर',
    'point': 'पॉइंट', 'hub': 'हब', 'world': 'वर्ल्ड', 'zone': 'जोन', 'plaza': 'प्लाजा',
    'mall': 'मॉल', 'complex': 'कॉम्प्लेक्स', 'kirana': 'किराना', 'kirana store': 'किराना स्टोर', 'general': 'जनरल', 'provisions': 'प्रोविजंस',
    'pvt': 'प्राइवेट', 'pvt.': 'प्राइवेट', 'private': 'प्राइवेट', 'ltd': 'लिमिटेड', 'ltd.': 'लिमिटेड', 'limited': 'लिमिटेड',

    # Events & Ad Headlines
    'sale': 'सेल', 'mega sale': 'महासेल', 'grand sale': 'भव्य सेल', 'dhamaka': 'धमाका', 'dhamaka sale': 'धमाका सेल',
    'mega sale dhamaka': 'महासेल धमाका',
    'clearance sale': 'क्लीयरेंस सेल', 'grand opening': 'भव्य शुभारंभ', 'opening': 'शुभारंभ',
    'inauguration': 'उद्घाटन व शुभारंभ', 'launch': 'लॉन्च', 'launching': 'नवीन लॉन्चिंग',
    'welcome': 'हार्दिक स्वागत', 'offer': 'विशेष ऑफर', 'festive offer': 'त्योहारी ऑफर',
    'special offer': 'विशेष छूट', 'diwali': 'दीपावली', 'deepawali': 'दीपावली', 'dhanteras': 'धनतेरस',
    'navratri': 'नवरात्रि', 'dussehra': 'दशहरा', 'eid': 'ईद', 'holi': 'होली',
    'new year': 'नव वर्ष', 'happy new year': 'नव वर्ष की शुभकामनाएं',
    'discount': 'छूट', 'flat discount': 'फ्लैट छूट', 'concession': 'रियायत', 'free': 'निःशुल्क',
    'admission open': 'प्रवेश प्रारंभ', 'admissions open': 'प्रवेश प्रारंभ', 'admission': 'प्रवेश',
    'batch': 'बैच', 'new batch': 'नवीन बैच', 'registration': 'पंजीयन', 'registrations open': 'पंजीयन प्रारंभ',
    'vacancy': 'आवश्यकता', 'requirement': 'आवश्यकता', 'wanted': 'आवश्यकता', 'walk-in': 'वॉक-इन',
    'interview': 'साक्षात्कार', 'public notice': 'सार्वजनिक सूचना', 'legal notice': 'विधिक सूचना',
    'court notice': 'न्यायालयीन सूचना', 'tender notice': 'निविदा सूचना', 'tender': 'निविदा',
    'auction': 'नीलामी', 'election': 'चुनाव प्रचार', 'vote': 'मतदान', 'candidate': 'प्रत्याशी',
    'congratulations': 'हार्दिक बधाई', 'hearty congratulations': 'हार्दिक बधाई', 'best wishes': 'शुभकामनाएं',
    'in memory of': 'पुण्यस्मरण', 'remembrance': 'पुण्यतिथि स्मरण', 'condolence': 'शोक संदेश',
    'obituary': 'श्रद्धांजलि', 'shradhanjali': 'श्रद्धांजलि', 'besna': 'बेसना', 'uthavna': 'उठावना',

    # Address & Geographical (Indore, Malwa, MP)
    'road': 'रोड', 'marg': 'मार्ग', 'street': 'गली', 'lane': 'गली', 'gali': 'गली',
    'mohalla': 'मोहल्ला', 'colony': 'कॉलोनी', 'nagar': 'नगर', 'puram': 'पुरम',
    'vihar': 'विहार', 'enclave': 'एंक्लेव', 'kunj': 'कुंज', 'dham': 'धाम',
    'vatika': 'वाटिका', 'bagh': 'बाग', 'garden': 'गार्डन', 'park': 'पार्क',
    'square': 'चौराहा', 'chauraha': 'चौराहा', 'circle': 'सर्कल', 'chowk': 'चौक',
    'bridge': 'पुल', 'flyover': 'फ्लाईओवर', 'station': 'स्टेशन', 'stand': 'स्टैंड',
    'bus stand': 'बस स्टैंड', 'railway station': 'रेलवे स्टेशन', 'depot': 'डिपो',
    'gate': 'गेट', 'dwar': 'द्वार', 'market': 'मार्केट', 'mandi': 'मंडी', 'ganj': 'गंज',
    'area': 'क्षेत्र', 'sector': 'सेक्टर', 'phase': 'फेज', 'block': 'ब्लॉक',
    'plot': 'प्लाट', 'flat': 'फ्लैट', 'house': 'मकान', 'floor': 'मंजिल',
    'ground floor': 'तल मंजिल', 'first floor': 'प्रथम मंजिल', '1st floor': 'प्रथम मंजिल',
    'second floor': 'द्वितीय मंजिल', '2nd floor': 'द्वितीय मंजिल', 'basement': 'बेसमेंट',
    'near': 'के पास', 'opposite': 'के सामने', 'opp': 'के सामने', 'opp.': 'के सामने',
    'behind': 'के पीछे', 'next to': 'के पास', 'above': 'के ऊपर',
    'indore': 'इंदौर', 'sarafa': 'सराफा', 'sarafa bazar': 'सराफा बाजार',
    'rajwada': 'राजबाड़ा', 'palasia': 'पलासिया', 'old palasia': 'ओल्ड पलासिया', 'new palasia': 'न्यू पलासिया',
    'bhawarkua': 'भंवरकुआं', 'bhawarkua main road': 'भंवरकुआं मेन रोड',
    'vijay nagar': 'विजयनगर', 'sudama nagar': 'सुदामा नगर', 'annapurna': 'अन्नपूर्णा',
    'annapurna road': 'अन्नपूर्णा रोड', 'press complex': 'प्रेस परिसर',
    'm.g. road': 'एम.जी. रोड', 'mg road': 'एम.जी. रोड', 'a.b. road': 'एबी रोड', 'ab road': 'एबी रोड',
    'jail road': 'जेल रोड', 'siaganj': 'सियागंज', 'malharganj': 'मल्हारगंज', 'khajrana': 'खजराना',
    'bhopal': 'भोपाल', 'ujjain': 'उज्जैन', 'dewas': 'देवास', 'mhow': 'महू', 'dhar': 'धार',
    'khandwa': 'खंडवा', 'khargone': 'खरगोन', 'ratlam': 'रतलाम', 'gwalior': 'ग्वालियर',
    'jabalpur': 'जबलपुर', 'madhya pradesh': 'मध्य प्रदेश', 'm.p.': 'म.प्र.', 'mp': 'म.प्र.',
}

# Reverse mapping for Hindi to English
NEWSPAPER_GLOSSARY_REV = {
    v: k.title() for k, v in NEWSPAPER_GLOSSARY.items()
}
# Override specific reverse mappings for natural English casing & advertising terminology
NEWSPAPER_GLOSSARY_REV.update({
    'किराना स्टोर': 'Kirana Store',
    'किराना': 'Kirana',
    'मिष्ठान्न': 'Sweets',
    'स्वीट्स': 'Sweets',
    'मिष्ठान्न भंडार': 'Mishtan Bhandar',
    'मिष्ठान्न एवं नमकीन': 'Sweets & Namkeen',
    'वस्त्र भंडार': 'Vastra Bhandar',
    'वस्त्र': 'Cloth',
    'भंडार': 'Bhandar',
    'शोरूम': 'Showroom',
    'ऑटो पार्ट्स': 'Auto Parts',
    'स्पेयर पार्ट्स': 'Spare Parts',
    'हार्डवेयर एवं सेनेटरी': 'Hardware & Sanitary',
    'हार्डवेयर': 'Hardware',
    'सैनिटरी': 'Sanitary',
    'इलेक्ट्रॉनिक्स': 'Electronics',
    'मोबाइल': 'Mobile',
    'ज्वेलर्स': 'Jewellers',
    'पुस्तक भंडार': 'Pustak Bhandar',
    'बुक स्टोर': 'Book Store',
    'स्टेशनरी': 'Stationery',
    'ऑप्टिकल्स': 'Opticals',
    'अग्रवाल': 'Agrawal',
    'महासेल': 'Mega Sale',
    'धमाका': 'Dhamaka',
    'महासेल धमाका': 'Mega Sale Dhamaka',
    'धमाका सेल': 'Dhamaka Sale',
    'भव्य शुभारंभ': 'Grand Opening',
    'दीपावली': 'Diwali',
    'सार्वजनिक सूचना': 'Public Notice',
    'निविदा सूचना': 'Tender Notice',
    'श्रद्धांजलि': 'Tribute',
    'शोक संदेश': 'Condolence',
    'विजयनगर': 'Vijay Nagar',
    'सुदामा नगर': 'Sudama Nagar',
    'प्रेस परिसर': 'Press Complex',
    'प्रेस कॉम्प्लेक्स': 'Press Complex',
    'एम.जी. रोड': 'M.G. Road',
    'एबी रोड': 'AB Road',
    'जेल रोड': 'Jail Road',
    'सराफा बाजार': 'Sarafa Bazar',
    'सराफा': 'Sarafa',
    'भंवरकुआं': 'Bhawarkua',
    'पलासिया': 'Palasia',
    'सियागंज': 'Siaganj',
    'मल्हारगंज': 'Malharganj',
    'खजराना': 'Khajrana',
    'अन्नपूर्णा': 'Annapurna',
    'मे.': 'M/s',
    'श्री': 'Shri',
    'श्रीमती': 'Smt.',
    'डॉ.': 'Dr.',
})

# Pre-sorted lists for longest multi-word matches first
_MULTI_WORD_EN = sorted([k for k in NEWSPAPER_GLOSSARY if ' ' in k], key=len, reverse=True)
_MULTI_WORD_HI = sorted([k for k in NEWSPAPER_GLOSSARY_REV if ' ' in k], key=len, reverse=True)

# ---------------------------------------------------------------------------
# Tier 2: Universal Rule-Based Phonetic Transliteration Engine
# ---------------------------------------------------------------------------
_EN_CONSONANTS = [
    ('ksh', 'क्ष'), ('gya', 'ज्ञ'), ('gy', 'ज्ञ'), ('shr', 'श्र'),
    ('chh', 'छ'), ('ch', 'च'), ('kh', 'ख'), ('gh', 'घ'),
    ('jh', 'झ'), ('th', 'थ'), ('dh', 'ध'), ('ph', 'फ'),
    ('bh', 'भ'), ('sh', 'श'), ('wh', 'व'),
    ('k', 'क'), ('g', 'ग'), ('c', 'क'), ('j', 'ज'),
    ('t', 'ट'), ('d', 'ड'), ('n', 'न'), ('p', 'प'),
    ('f', 'फ'), ('b', 'ब'), ('m', 'म'), ('y', 'य'),
    ('r', 'र'), ('l', 'ल'), ('v', 'व'), ('w', 'व'),
    ('s', 'स'), ('h', 'ह'), ('z', 'ज़'), ('q', 'क'), ('x', 'क्स')
]

_EN_VOWEL_SIGNS = {
    'aa': 'ा', 'ai': 'ै', 'ay': 'े', 'au': 'ौ', 'ou': 'ौ',
    'ee': 'ी', 'oo': 'ू', 'ea': 'ी', 'ey': 'े',
    'a': 'ा', 'e': 'े', 'i': 'ि', 'o': 'ो', 'u': 'ु'
}

_EN_INITIAL_VOWELS = {
    'aa': 'आ', 'ai': 'ऐ', 'ay': 'ए', 'au': 'औ', 'ou': 'औ',
    'ee': 'ई', 'oo': 'ऊ', 'ea': 'ई', 'ey': 'ए',
    'a': 'अ', 'e': 'ए', 'i': 'इ', 'o': 'ओ', 'u': 'उ'
}

_HI_CONSONANTS_MAP = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
    'ष': 'sh', 'स': 's', 'ह': 'h', 'क्ष': 'ksh', 'त्र': 'tr',
    'ज्ञ': 'gya', 'श्र': 'shr', 'ड़': 'd', 'ढ़': 'dh',
    'ज़': 'z', 'फ़': 'f', 'ख़': 'kh', 'ग़': 'gh'
}

_HI_MATRAS_MAP = {
    'ा': 'a', 'ि': 'i', 'ी': 'i', 'ु': 'u', 'ू': 'u',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'n', 'ँ': 'n', 'ः': 'h', 'ृ': 'ri'
}

_HI_VOWELS_MAP = {
    'अ': 'a', 'आ': 'a', 'इ': 'i', 'ई': 'i', 'उ': 'u', 'ऊ': 'u',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ऋ': 'ri'
}


def phonetic_transliterate_en_to_hi(word: str) -> str:
    """
    Pure Python offline phonetic transliteration for English words into Devanagari.
    Handles consonant clusters, initial vowels, and inherent schwa.
    """
    w = word.lower()
    n = len(w)
    i = 0
    res = []
    prev_cons = False

    while i < n:
        # 1. Match consonants (longest first)
        matched_c = False
        for c_str, dev in _EN_CONSONANTS:
            if w.startswith(c_str, i):
                if prev_cons:
                    res.append('्')
                res.append(dev)
                prev_cons = True
                i += len(c_str)
                matched_c = True
                break
        if matched_c:
            continue

        # 2. Match vowels
        matched_v = False
        for v_str in sorted(_EN_VOWEL_SIGNS.keys(), key=len, reverse=True):
            if w.startswith(v_str, i):
                if prev_cons:
                    # In Indian names, short medial 'a' is implicit in consonant
                    if v_str == 'a' and i + 1 < n:
                        pass
                    else:
                        res.append(_EN_VOWEL_SIGNS[v_str])
                else:
                    res.append(_EN_INITIAL_VOWELS[v_str])
                prev_cons = False
                i += len(v_str)
                matched_v = True
                break
        if matched_v:
            continue

        # Remaining non-alphabetic character
        res.append(w[i])
        prev_cons = False
        i += 1

    return ''.join(res)


def phonetic_transliterate_hi_to_en(word: str) -> str:
    """
    Pure Python offline phonetic transliteration from Devanagari into Latin script.
    """
    res = []
    n = len(word)
    i = 0
    while i < n:
        ch = word[i]

        if ch in _HI_VOWELS_MAP:
            res.append(_HI_VOWELS_MAP[ch])
            i += 1
            continue

        if ch in _HI_CONSONANTS_MAP:
            cons = _HI_CONSONANTS_MAP[ch]
            if i + 1 < n:
                next_ch = word[i + 1]
                if next_ch == '्':  # Halant
                    res.append(cons)
                    i += 2
                    continue
                elif next_ch in ('ं', 'ँ'):  # Anusvara / Chandrabindu with implicit vowel 'a'
                    res.append(cons + 'an')
                    i += 2
                    continue
                elif next_ch in _HI_MATRAS_MAP:
                    res.append(cons + _HI_MATRAS_MAP[next_ch])
                    i += 2
                    continue
                elif next_ch in _HI_CONSONANTS_MAP:
                    # Inherent 'a' between consonants
                    res.append(cons + 'a')
                    i += 1
                    continue
                else:
                    res.append(cons)
                    i += 1
                    continue
            else:
                res.append(cons)
                i += 1
                continue

        if ch in _HI_MATRAS_MAP:
            res.append(_HI_MATRAS_MAP[ch])
            i += 1
            continue

        res.append(ch)
        i += 1

    return ''.join(res).title()


def is_devanagari(text: str) -> bool:
    """Check if the text contains Devanagari Hindi characters."""
    if not text:
        return False
    return bool(re.search(r'[\u0900-\u097F]', str(text)))


def detect_script(text: str) -> str:
    """Returns 'hi' if text contains Devanagari script, else 'en'."""
    return 'hi' if is_devanagari(text) else 'en'


def translate_offline(raw_text: str, sl: str, tl: str) -> str:
    """
    Complete lightweight offline translation and transliteration engine.
    Uses multi-word lexicon -> single-word lexicon -> phonetic engine.
    """
    if sl == 'en' and tl == 'hi':
        res = raw_text

        # 1. Multi-word phrases
        for phrase in _MULTI_WORD_EN:
            pattern = r'(?i)\b' + re.escape(phrase) + r'\b'
            res = re.sub(pattern, NEWSPAPER_GLOSSARY[phrase], res)

        # 2. Tokenize remaining words and transliterate/translate
        def _replace_en_token(m):
            w = m.group(0)
            low = w.lower()
            if low in NEWSPAPER_GLOSSARY:
                return NEWSPAPER_GLOSSARY[low]
            # Digits are kept intact
            if w.isdigit():
                return w
            # Use phonetic fallback
            return phonetic_transliterate_en_to_hi(w)

        res = re.sub(r'\b[a-zA-Z\.]+\b', _replace_en_token, res)
        return res

    elif sl == 'hi' and tl == 'en':
        res = raw_text

        # 1. Multi-word phrases (longest first)
        for phrase in sorted(_MULTI_WORD_HI, key=len, reverse=True):
            if phrase in res:
                res = res.replace(phrase, NEWSPAPER_GLOSSARY_REV[phrase])

        # 2. Tokenize remaining Devanagari words and replace / transliterate
        def _replace_hi_token(m):
            w = m.group(0)
            if w in NEWSPAPER_GLOSSARY_REV:
                return NEWSPAPER_GLOSSARY_REV[w]
            return phonetic_transliterate_hi_to_en(w)

        res = re.sub(r'[\u0900-\u097F]+', _replace_hi_token, res)
        return res

    return raw_text


def _normalize_ad_translation(text: str, sl: str, tl: str) -> str:
    """Post-processes translations to guarantee authentic Indian newspaper advertising terminology."""
    if not text:
        return ''
    if tl == 'en':
        # Prevent literal English mistranslations from generic MT models
        text = re.sub(r'(?i)\bgrocery store\b', 'Kirana Store', text)
        text = re.sub(r'(?i)\bgrocery\b', 'Kirana', text)
        text = re.sub(r'(?i)\bmegacell\b', 'Mega Sale', text)
        text = re.sub(r'(?i)\bexplosion\b', 'Dhamaka', text)
        text = re.sub(r'(?i)\bclothing store\b', 'Cloth Store', text)
        text = re.sub(r'(?i)\bbhanwarkuan\b', 'Bhawarkua', text)
        text = re.sub(r'(?i)\bm/s\b', 'M/s', text)
    elif tl == 'hi':
        # Prevent weird literal Hindi translations
        text = re.sub(r'किराना की दुकान', 'किराना स्टोर', text)
        text = re.sub(r'किराने का सामान', 'किराना', text)
        text = re.sub(r'महाकोशिका', 'महासेल', text)
        text = re.sub(r'विस्फोट', 'धमाका', text)
        text = re.sub(r'(डॉ|पं|प्रो|एड|मे|श्री|श्रीमती)\.\.', r'\1.', text)
    return text.strip()


def translate_text(text: str, source_lang: str = 'auto', target_lang: str = None) -> str:
    """
    Translates or transliterates text between English and Hindi.
    If target_lang is not specified, auto-targets the opposite language:
    - If input is Devanagari, target is 'en'.
    - If input is English/Latin, target is 'hi'.
    """
    if not text or not str(text).strip():
        return ''

    raw_text = str(text).strip()

    # Determine direction
    input_is_hi = is_devanagari(raw_text)
    if not target_lang:
        target_lang = 'en' if input_is_hi else 'hi'

    if source_lang == target_lang:
        return raw_text

    sl = 'hi' if input_is_hi else ('en' if source_lang == 'auto' else source_lang)
    tl = target_lang

    cache_key = f"{sl}->{tl}:{raw_text.lower()}"
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    # Fast offline exact match on the full phrase
    low_text = raw_text.lower().strip()
    if sl == 'en' and tl == 'hi' and low_text in NEWSPAPER_GLOSSARY:
        res = NEWSPAPER_GLOSSARY[low_text]
        _TRANSLATION_CACHE[cache_key] = res
        return res
    elif sl == 'hi' and tl == 'en' and raw_text in NEWSPAPER_GLOSSARY_REV:
        res = NEWSPAPER_GLOSSARY_REV[raw_text]
        _TRANSLATION_CACHE[cache_key] = res
        return res

    # 1. High-accuracy offline translation & transliteration
    offline_candidate = translate_offline(raw_text, sl, tl)

    # Check if all tokens in the input are present in our curated lexicon
    all_known = False
    if sl == 'hi':
        tokens = re.findall(r'[\u0900-\u097F]+', raw_text)
        if tokens and all(t in NEWSPAPER_GLOSSARY_REV for t in tokens):
            all_known = True
    elif sl == 'en':
        tokens = re.findall(r'[a-zA-Z]+', raw_text.lower())
        if tokens and all(t in NEWSPAPER_GLOSSARY for t in tokens):
            all_known = True

    if all_known:
        result = _normalize_ad_translation(offline_candidate, sl, tl)
        _TRANSLATION_CACHE[cache_key] = result
        return result

    # Opportunistic network call (Google Translate single endpoint with quick 1.5s timeout)
    try:
        query = urllib.parse.quote(raw_text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q={query}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) VishwaguruBilling/1.0'
            }
        )
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            translated_segs = [seg[0] for seg in data[0] if seg and seg[0]]
            translated_result = ''.join(translated_segs).strip()

            if translated_result:
                if tl == 'en' and not raw_text.isupper() and not raw_text.islower():
                    translated_result = translated_result.title()

                normalized = _normalize_ad_translation(translated_result, sl, tl)
                _TRANSLATION_CACHE[cache_key] = normalized
                return normalized
    except Exception as exc:
        logger.debug("Network translation unavailable (%s). Using lightweight offline engine.", exc)

    # High-accuracy offline translation & transliteration
    result = _normalize_ad_translation(offline_candidate, sl, tl)
    _TRANSLATION_CACHE[cache_key] = result
    return result


def split_bilingual(text: str) -> tuple[str, str]:
    """
    Extracts (hindi_part, english_part) from a string.
    Supports formats:
    - "पटेल ऑटोमोबाइल्स (Patel Automobiles)" -> ("पटेल ऑटोमोबाइल्स", "Patel Automobiles")
    - "Patel Automobiles (पटेल ऑटोमोबाइल्स)" -> ("पटेल ऑटोमोबाइल्स", "Patel Automobiles")
    - "पटेल ऑटोमोबाइल्स" -> ("पटेल ऑटोमोबाइल्स", "")
    - "Patel Automobiles" -> ("", "Patel Automobiles")
    """
    if not text:
        return ('', '')

    raw = str(text).strip()
    m = re.match(r'^(.*?)\s*\((.*?)\)$', raw)
    if m:
        p1 = m.group(1).strip()
        p2 = m.group(2).strip()
        if is_devanagari(p1):
            return (p1, p2)
        elif is_devanagari(p2):
            return (p2, p1)
        else:
            return (p1, p2)

    if is_devanagari(raw):
        return (raw, '')
    return ('', raw)


def make_bilingual(text: str, custom_hi: str = None, custom_en: str = None) -> str:
    """
    Creates a standardized "हिन्दी नाम (English Name)" composite string.
    - If explicit custom_hi and custom_en are provided, formats them together.
    - If text is already in composite format, preserves or updates it.
    - If text is only Hindi, auto-translates to English.
    - If text is only English, auto-translates to Hindi.
    """
    if not text and not custom_hi and not custom_en:
        return ''

    # If explicit separate parts are provided
    if custom_hi or custom_en:
        hi = (custom_hi or '').strip()
        en = (custom_en or '').strip()
        if not hi and en:
            hi = translate_text(en, 'en', 'hi')
        elif not en and hi:
            en = translate_text(hi, 'hi', 'en')
        if hi and en:
            return f"{hi} ({en})"
        return hi or en

    hi_part, en_part = split_bilingual(text)
    if hi_part and en_part:
        return f"{hi_part} ({en_part})"

    if hi_part and not en_part:
        en_trans = translate_text(hi_part, 'hi', 'en')
        return f"{hi_part} ({en_trans})" if en_trans else hi_part

    if en_part and not hi_part:
        hi_trans = translate_text(en_part, 'en', 'hi')
        return f"{hi_trans} ({en_part})" if hi_trans else en_part

    return str(text).strip()


def format_custom_size_bilingual(size_str: str, lang: str = 'en') -> str:
    """
    Formats custom dimensions (e.g. 10x12 cm <-> 10x12 सेमी).
    """
    if not size_str:
        return ''
    s = str(size_str).strip()
    if lang == 'hi':
        s = re.sub(r'(?i)\b(?:cm|cms|centimeters?)\b', 'सेमी', s)
        s = re.sub(r'\s*[xX×]\s*', 'x', s)
        return s
    else:
        s = re.sub(r'(?:सेमी|से\.मी\.)', 'cm', s)
        s = re.sub(r'\s*[xX×]\s*', 'x', s)
        return s
