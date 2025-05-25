import json

senttag2opinion = {'pos': 'great', 'neg': 'bad', 'neu': 'ok', 'con':'conflict'} 
sentword2opinion = {'positive': 'great', 'negative': 'bad', 'neutral': 'ok'}
ACE05_event_type_list = ['Business.Declare-Bankruptcy', 'Business.End-Org', 'Business.Merge-Org', 'Business.Start-Org', 
                         'Conflict.Attack', 'Conflict.Demonstrate', 'Contact.Meet', 'Contact.Phone-Write', 
                         'Justice.Acquit', 'Justice.Appeal', 'Justice.Arrest-Jail', 'Justice.Charge-Indict', 'Justice.Convict', 
                         'Justice.Execute', 'Justice.Extradite', 'Justice.Fine', 'Justice.Pardon', 'Justice.Release-Parole', 
                         'Justice.Sentence', 'Justice.Sue', 'Justice.Trial-Hearing', 
                         'Life.Be-Born', 'Life.Die', 'Life.Divorce', 'Life.Injure', 'Life.Marry', 
                         'Movement.Transport', 'Personnel.Elect', 'Personnel.End-Position', 'Personnel.Nominate', 
                         'Personnel.Start-Position', 'Transaction.Transfer-Money', 'Transaction.Transfer-Ownership']


ACE05_event_type_argument_role_dict = {'Business.Declare-Bankruptcy': ['organization', 'place'], 'Business.End-Org': ['organization', 'place'], 'Business.Merge-Org': ['organization'], 
                                       'Business.Start-Org': ['agent', 'organization', 'place'], 'Conflict.Attack': ['attacker', 'instrument', 'place', 'target', 'victim'], 
                                       'Conflict.Demonstrate': ['entity', 'place'], 'Contact.Meet': ['entity', 'place'], 'Contact.Phone-Write': ['entity', 'place'], 
                                       'Justice.Acquit': ['adjudicator', 'defendant'], 'Justice.Appeal': ['adjudicator', 'place', 'plaintiff'], 
                                       'Justice.Arrest-Jail': ['agent', 'person', 'place'], 'Justice.Charge-Indict': ['adjudicator', 'defendant', 'place', 'prosecutor'], 
                                       'Justice.Convict': ['adjudicator', 'defendant', 'place'], 'Justice.Execute': ['agent', 'person', 'place'], 
                                       'Justice.Extradite': ['agent', 'destination', 'origin'], 'Justice.Fine': ['adjudicator', 'entity', 'place'], 
                                       'Justice.Pardon': ['adjudicator', 'defendant', 'place'], 'Justice.Release-Parole': ['entity', 'person', 'place'], 
                                       'Justice.Sentence': ['adjudicator', 'defendant', 'place'], 'Justice.Sue': ['adjudicator', 'defendant', 'place', 'plaintiff'], 
                                       'Justice.Trial-Hearing': ['adjudicator', 'defendant', 'place', 'prosecutor'], 'Life.Be-Born': ['person', 'place'], 
                                       'Life.Die': ['agent', 'instrument', 'person', 'place', 'victim'], 'Life.Divorce': ['person', 'place'], 
                                       'Life.Injure': ['agent', 'instrument', 'place', 'victim'], 'Life.Marry': ['person', 'place'], 
                                       'Movement.Transport': ['agent', 'artifact', 'destination', 'origin', 'place', 'vehicle'], 'Personnel.Elect': ['entity', 'person', 'place'], 
                                       'Personnel.End-Position': ['entity', 'person', 'place'], 'Personnel.Nominate': ['agent', 'person'], 
                                       'Personnel.Start-Position': ['entity', 'person', 'place'], 'Transaction.Transfer-Money': ['beneficiary', 'giver', 'place', 'recipient'], 
                                       'Transaction.Transfer-Ownership': ['artifact', 'beneficiary', 'buyer', 'place', 'seller']}


ACE05_argument_role_list = ['adjudicator', 'agent', 'artifact', 'attacker', 'beneficiary', 'buyer', 'defendant', 'destination', 'entity', 'giver', 'instrument', 'organization', 'origin', 'person', 'place', 
                                       'plaintiff', 'prosecutor', 'recipient', 'seller', 'target', 'vehicle', 'victim', "null"] 
argument_role_map = {'Adjudicator': 'adjudicator', 'Agent': 'agent', 'Artifact': 'artifact', 'Attacker': 'attacker', 'Beneficiary': 'beneficiary', 'Buyer': 'buyer', 'Defendant': 'defendant', 'Destination': 'destination', 'Entity': 'entity', 'Giver': 'giver', 
'Instrument': 'instrument', 'Org': 'organization', 'Origin': 'origin', 'Person': 'person', 'Place': 'place', 'Plaintiff': 'plaintiff', 'Prosecutor': 'prosecutor', 'Recipient': 'recipient', 'Seller': 'seller', 'Target': 'target', 'Vehicle': 'vehicle', 'Victim': 'victim'}
ACE05_event_description_dict = {
    "Movement.Transport": "agent ( and agent ) transported artifact ( and artifact ) in vehicle ( and vehicle ) cost price from origin place ( and origin ) to destination place ( and destination , destination )",
    "Personnel.Elect": "entity ( and entity ) elected person ( and person ) at place ( and place ) for position",
    "Personnel.Start-Position": "person ( and person ) started working at entity organization ( and entity organization ) at place ( and place ) for position",
    "Personnel.Nominate": "agent ( and agent ) nominated person with position at place ( and place )",
    "Personnel.End-Position": "person ( and person ) stopped working at position of entity organization ( and entity organization ) at place ( and place )",
    "Conflict.Attack": "attacker ( and attacker ) attacked target ( and target ) hurting victims using instrument ( and instrument ) at place ( and place )",
    "Conflict.Demonstrate": "entity ( and entity ) demonstrated at place ( and place )",
    "Contact.Meet": "entity ( and entity ) met with entity ( and entity ) at place ( and place )",
    "Contact.Phone-Write": "entity ( and entity ) communicated remotely with entity ( and entity ) at place ( and place )",
    "Transaction.Transfer-Ownership": "seller gave buyer ( and buyer ) to beneficiary ( and beneficiary ) for the benefit of artifact ( and artifact ) cost price at place ( and place )",
    "Transaction.Transfer-Money": "giver ( and giver ) gave money to recipient ( and recipient ) for the benefit of beneficiary ( and beneficiary ) at place ( and place )",
    "Justice.Arrest-Jail": "agent ( and agent ) arrested person ( and person ) at place ( and place ) for crime",
    "Justice.Release-Parole": "entity ( and entity ) released or paroled person ( and person ) at place ( and place ) for crime",
    "Justice.Trial-Hearing": "prosecutor tried defendant ( and defendant ) before adjudicator ( and adjudicator ) court or judge for crime at place ( and place )",
    "Justice.Charge-Indict": "prosecutor ( and prosecutor ) charged or indicted defendant ( and defendant ) before adjudicator ( and adjudicator ) court or judge for crime at place ( and place )",    
    "Justice.Sue": "plaintiff ( and plaintiff ) sued defendant ( and defendant ) before adjudicator ( and adjudicator ) court or judge at place ( and place ) for crime",
    "Justice.Convict": "adjudicator ( and adjudicator ) court or judge convicted defendant ( and defendant ) at place ( and place ) for crime",
    "Justice.Sentence": "adjudicator ( and adjudicator ) court or judge sentenced to sentence of defendant ( and defendant ) at place ( and place ) for crime",
    "Justice.Fine": "adjudicator ( and adjudicator ) court or judge fined entity ( and entity ) at place ( and place ) for crime cost money",
    "Justice.Execute": "agent ( and agent ) executed person at place ( and place ) for crime",
    "Justice.Extradite": "agent ( and agent ) extradited person from origin place to destination place for crime",
    "Justice.Acquit": "adjudicator ( and adjudicator ) court or judge acquitted defendant ( and defendant ) for crime at place ( and place )",
    "Justice.Pardon": "adjudicator ( and adjudicator ) court or judge pardoned defendant ( and defendant ) at place ( and place ) for crime",
    "Justice.Appeal": "plaintiff ( and plaintiff ) sued defendant ( and defendant ) appealed to adjudicator ( and adjudicator ) court or judge at place ( and place )",
    "Business.Start-Org": "agent ( and agent ) started organization ( and organization ) at place ( and place )",
    "Business.Merge-Org": "organization merged with organization at place ( and place )",
    "Business.End-Org": "organization ( and organization ) shut down at place ( and place )",
    "Business.Declare-Bankruptcy": "organization ( and organization ) declared bankruptcy at place ( and place )",
    "Life.Be-Born": "person ( and person ) was born at place ( and place )",
    "Life.Marry": "person married person at place ( and place )",
    "Life.Divorce": "person divorced person at place ( and place )",
    "Life.Injure": "agent ( and agent ) injured victim ( and victim ) with instrument ( and instrument ) at place ( and place )",
    "Life.Die": "agent ( and agent ) killed victim ( and victim ) with instrument ( and instrument ) at place ( and place )"
}


ere_event_type_list = ['Business:Declare-Bankruptcy', 'Business:End-Org', 'Business:Merge-Org', 'Business:Start-Org', 'Conflict:Attack', 'Conflict:Demonstrate', 'Contact:Broadcast', 'Contact:Contact', 'Contact:Correspondence', 'Contact:Meet', 'Justice:Acquit', 'Justice:Appeal', 'Justice:Arrest-Jail', 'Justice:Charge-Indict', 'Justice:Convict', 'Justice:Execute', 'Justice:Extradite', 'Justice:Fine', 'Justice:Pardon', 'Justice:Release-Parole', 'Justice:Sentence', 'Justice:Sue', 'Justice:Trial-Hearing', 'Life:Be-Born', 'Life:Die', 'Life:Divorce', 'Life:Injure', 'Life:Marry', 'Manufacture:Artifact', 'Movement:Transport-Artifact', 
'Movement:Transport-Person', 'Personnel:Elect', 'Personnel:End-Position', 'Personnel:Nominate', 'Personnel:Start-Position', 'Transaction:Transaction', 'Transaction:Transfer-Money', 'Transaction:Transfer-Ownership']
ere_argument_role_list = ['adjudicator', 'agent', 'artifact', 'attacker', 'audience', 'beneficiary', 'defendant', 'destination', 'entity', 'giver', 'instrument', 'organization', 'origin', 'person', 'place', 'plaintiff', 'prosecutor', 'recipient', 'target', 'thing', 'victim']
ere_argument_role_map = {'Adjudicator': 'adjudicator', 'Agent': 'agent', 'Artifact': 'artifact', 'Attacker': 'attacker', 'Audience': 'audience', 'Beneficiary': 'beneficiary', 'Defendant': 'defendant', 'Destination': 'destination', 'Entity': 'entity', 'Giver': 'giver', \
                 'Instrument': 'instrument', 'Org': 'organization', 'Origin': 'origin', 'Person': 'person', 'Place': 'place', 'Plaintiff': 'plaintiff', 'Prosecutor': 'prosecutor', 'Recipient': 'recipient', 'Target': 'target', 'Thing': 'thing', 'Victim': 'victim'}


ere_event_type_argument_role_dict = {
    'Business:Declare-Bankruptcy': ['organization'],
    'Business:End-Org': ['organization', 'place'],
    'Business:Merge-Org': ['organization'],
    'Business:Start-Org': ['agent', 'organization', 'place'],
    'Conflict:Attack': ['attacker', 'instrument', 'place', 'target'], 
    'Conflict:Demonstrate': ['entity', 'place'],
    'Contact:Broadcast': ['audience', 'entity', 'place'], 
    'Contact:Contact': ['entity', 'place'], 
    'Contact:Correspondence': ['entity', 'place'], 
    'Contact:Meet': ['entity', 'place'], 
    'Justice:Acquit': ['adjudicator', 'defendant', 'place'], 
    'Justice:Appeal': ['adjudicator', 'defendant', 'prosecutor'], 
    'Justice:Arrest-Jail': ['agent', 'person', 'place'],
    'Justice:Charge-Indict': ['adjudicator', 'defendant', 'place', 'prosecutor'],
    'Justice:Convict': ['adjudicator', 'defendant', 'place'],
    'Justice:Execute': ['agent', 'person', 'place'],
    'Justice:Extradite': ['agent', 'destination', 'origin', 'person'], 
    'Justice:Fine': ['adjudicator', 'entity', 'place'],
    'Justice:Pardon': ['adjudicator', 'defendant', 'place'],
    'Justice:Release-Parole': ['agent', 'person', 'place'],  
    'Justice:Sentence': ['adjudicator', 'defendant', 'place'],
    'Justice:Sue': ['adjudicator', 'defendant', 'place', 'plaintiff'],
    'Justice:Trial-Hearing': ['adjudicator', 'defendant', 'place', 'prosecutor'],
    'Life:Be-Born': ['person', 'place'],
    'Life:Die': ['agent', 'instrument', 'place', 'victim'], 
    'Life:Divorce': ['person', 'place'],
    'Life:Injure': ['agent', 'instrument', 'place', 'victim'],
    'Life:Marry': ['person', 'place'],
    'Manufacture:Artifact': ['agent', 'artifact', 'place'], 
    'Movement:Transport-Artifact': ['agent', 'artifact', 'destination', 'origin'], 
    'Movement:Transport-Person': ['agent', 'destination', 'instrument', 'origin', 'person'], 
    'Personnel:Elect': ['agent', 'person', 'place'], 
    'Personnel:End-Position': ['entity', 'person', 'place'],
    'Personnel:Nominate': ['agent', 'person', 'place'], 
    'Personnel:Start-Position': ['entity', 'person', 'place'],
    'Transaction:Transaction': ['beneficiary', 'giver', 'place', 'recipient'], 
    'Transaction:Transfer-Money': ['beneficiary', 'giver', 'place', 'recipient'],
    'Transaction:Transfer-Ownership': ['beneficiary', 'giver', 'place', 'recipient', 'thing'], 
}
ere_event_description_dict = {
    "Personnel:Elect": "entity ( and entity ) elected person ( and person ) at place ( and place ) for position",
    "Personnel:Start-Position": "person ( and person ) started working at entity organization ( and entity organization ) at place ( and place ) for position",
    "Personnel:Nominate": "agent ( and agent ) nominated person with position at place ( and place )",
    "Personnel:End-Position": "person ( and person ) stopped working at position of entity organization ( and entity organization ) at place ( and place )",
    "Conflict:Attack": "attacker ( and attacker ) attacked target ( and target ) hurting victims using instrument ( and instrument ) at place ( and place )",
    "Conflict:Demonstrate": "entity ( and entity ) demonstrated at place ( and place )",
    "Contact:Meet": "entity ( and entity ) met with entity ( and entity ) at place ( and place )",
    "Contact:Broadcast": "entity ( and entity ) broadcasted to audience ( and audience ) at place ( and place ) ( in one-way communication method )", 
    "Contact:Contact": "entity ( and entity ) contacted entity ( and entity ) at place ( and place ) ( document does not specify in person or not, or one-way or not)", 
    "Contact:Correspondence": "entity ( and entity ) corresponded with entity ( and entity ) at place ( and place ) ( via communication media or messaging methods )", 
    "Manufacture:Artifact": "agent ( and agent ) manufactured artifact ( and artifact ) artifact at place ( and place )", 
    "Movement:Transport-Artifact": "agent ( and agent ) transported artifact ( and artifact ) from origin ( and origin ) to destination ( and destination )", 
    "Movement:Transport-Person": "agent ( and agent ) transported person ( and person ) from origin ( and origin ) to destination ( and destination ) using instrument ( and instrument )", 
    "Transaction:Transaction": "giver ( and giver ) gave (or lent, borrowed, stole) something to recipient ( and recipient ) at place ( and place )", 
    "Transaction:Transfer-Ownership": "giver ( and giver ) gave thing ( and thing ) to beneficiary ( and beneficiary ) for the benefit of artifact ( and artifact ) cost price at place ( and place )", 
    "Transaction:Transfer-Money": "giver ( and giver ) gave money to recipient ( and recipient ) for the benefit of beneficiary ( and beneficiary ) at place ( and place )",
    "Justice:Arrest-Jail": "agent ( and agent ) arrested person ( and person ) at place ( and place ) for crime",
    "Justice:Release-Parole": "entity ( and entity ) released or paroled person ( and person ) at place ( and place ) for crime",
    "Justice:Trial-Hearing": "prosecutor tried defendant ( and defendant ) before adjudicator ( and adjudicator ) court or judge for crime at place ( and place )",
    "Justice:Charge-Indict": "prosecutor ( and prosecutor ) charged or indicted defendant ( and defendant ) before adjudicator ( and adjudicator ) court or judge for crime at place ( and place )",    
    "Justice:Sue": "plaintiff ( and plaintiff ) sued defendant ( and defendant ) before adjudicator ( and adjudicator ) court or judge at place ( and place ) for crime",
    "Justice:Convict": "adjudicator ( and adjudicator ) court or judge convicted defendant ( and defendant ) at place ( and place ) for crime",
    "Justice:Sentence": "adjudicator ( and adjudicator ) court or judge sentenced to sentence of defendant ( and defendant ) at place ( and place ) for crime",
    "Justice:Fine": "adjudicator ( and adjudicator ) court or judge fined entity ( and entity ) at place ( and place ) for crime cost money",
    "Justice:Execute": "agent ( and agent ) executed person at place ( and place ) for crime",
    "Justice:Extradite": "agent ( and agent ) extradited person from origin place to destination place for crime",
    "Justice:Acquit": "adjudicator ( and adjudicator ) court or judge acquitted defendant ( and defendant ) for crime at place ( and place )",
    "Justice:Pardon": "adjudicator ( and adjudicator ) court or judge pardoned defendant ( and defendant ) at place ( and place ) for crime",
    "Justice:Appeal": "plaintiff ( and plaintiff ) sued defendant ( and defendant ) appealed to adjudicator ( and adjudicator ) court or judge at place ( and place )",
    "Business:Start-Org": "agent ( and agent ) started organization ( and organization ) at place ( and place )",
    "Business:Merge-Org": "organization merged with organization at place ( and place )",
    "Business:End-Org": "organization ( and organization ) shut down at place ( and place )",
    "Business:Declare-Bankruptcy": "organization ( and organization ) declared bankruptcy at place ( and place )",
    "Life:Be-Born": "person ( and person ) was born at place ( and place )",
    "Life:Marry": "person married person at place ( and place )",
    "Life:Divorce": "person divorced person at place ( and place )",
    "Life:Injure": "agent ( and agent ) injured victim ( and victim ) with instrument ( and instrument ) at place ( and place )",
    "Life:Die": "agent ( and agent ) killed victim ( and victim ) with instrument ( and instrument ) at place ( and place )"
    
}





wikievent_event_type_list = ['ArtifactExistence.DamageDestroyDisableDismantle.Damage', 'ArtifactExistence.DamageDestroyDisableDismantle.Destroy', 
                             'ArtifactExistence.DamageDestroyDisableDismantle.DisableDefuse', 'ArtifactExistence.DamageDestroyDisableDismantle.Dismantle', 
                             'ArtifactExistence.DamageDestroyDisableDismantle.Unspecified', 'ArtifactExistence.ManufactureAssemble.Unspecified', 'Cognitive.IdentifyCategorize.Unspecified', 
                             'Cognitive.Inspection.SensoryObserve', 'Cognitive.Research.Unspecified', 'Cognitive.TeachingTrainingLearning.Unspecified', 'Conflict.Attack.DetonateExplode', 
                             'Conflict.Attack.Unspecified', 'Conflict.Defeat.Unspecified', 'Conflict.Demonstrate.DemonstrateWithViolence', 'Conflict.Demonstrate.Unspecified', 
                             'Contact.Contact.Broadcast', 'Contact.Contact.Correspondence', 'Contact.Contact.Meet', 'Contact.Contact.Unspecified', 'Contact.RequestCommand.Broadcast', 
                             'Contact.RequestCommand.Correspondence', 'Contact.RequestCommand.Meet', 'Contact.RequestCommand.Unspecified', 'Contact.ThreatenCoerce.Broadcast', 
                             'Contact.ThreatenCoerce.Correspondence', 'Contact.ThreatenCoerce.Unspecified', 'Control.ImpedeInterfereWith.Unspecified', 'Disaster.Crash.Unspecified', 
                             'Disaster.DiseaseOutbreak.Unspecified', 'GenericCrime.GenericCrime.GenericCrime', 'Justice.Acquit.Unspecified', 'Justice.ArrestJailDetain.Unspecified', 
                             'Justice.ChargeIndict.Unspecified', 'Justice.Convict.Unspecified', 'Justice.InvestigateCrime.Unspecified', 'Justice.ReleaseParole.Unspecified', 
                             'Justice.Sentence.Unspecified', 'Justice.TrialHearing.Unspecified', 'Life.Die.Unspecified', 'Life.Infect.Unspecified', 'Life.Injure.Unspecified', 
                             'Medical.Intervention.Unspecified', 'Movement.Transportation.Evacuation', 'Movement.Transportation.IllegalTransportation', 'Movement.Transportation.PreventPassage', 
                             'Movement.Transportation.Unspecified', 'Personnel.EndPosition.Unspecified', 'Personnel.StartPosition.Unspecified', 'Transaction.Donation.Unspecified', 'Transaction.ExchangeBuySell.Unspecified']
wikievent_argument_role_list =  ['acquired entity', 'artifact', 'artifact money', 'attacker', 'body part', 'communicator', 'components', 'crash object', 'damager', 'damager destroyer', 'defeated', 'defendant', 'demonstrator', 'destination', 'destroyer', 'detainee', 'disabler', 'disease', 
                                 'dismantler', 'employee', 'explosive device', 'giver', 'identified object', 'identified role', 'identifier', 'impeder', 'injurer', 'instrument', 'investigator', 'jailer', 'judge court', 'killer', 'learner', 'manufacturer assembler', 'observed entity', 'observer', 
                                 'origin', 'participant', 'passenger artifact', 'patient', 'payment barter', 'perpetrator', 'place', 'place of employment', 'position', 'preventer', 'prosecutor', 'recipient', 'regulator', 'researcher', 'subject', 'target', 'teacher trainer', 'topic', 'transporter', 'treater', 'vehicle', 'victim', 'victor']


wikievent_event_type_argument_role_dict = {'ArtifactExistence.DamageDestroyDisableDismantle.Damage': ['artifact', 'damager', 'instrument', 'place'], 'ArtifactExistence.DamageDestroyDisableDismantle.Destroy': ['artifact', 'destroyer', 'instrument', 'place'], 'ArtifactExistence.DamageDestroyDisableDismantle.DisableDefuse': ['artifact', 'disabler', 'instrument'], 
                                           'ArtifactExistence.DamageDestroyDisableDismantle.Dismantle': ['artifact', 'components', 'dismantler', 'instrument', 'place'], 'ArtifactExistence.DamageDestroyDisableDismantle.Unspecified': ['artifact', 'damager destroyer', 'instrument', 'place'], 'ArtifactExistence.ManufactureAssemble.Unspecified': ['artifact', 'components', 'manufacturer assembler', 'place'], 
                                           'Cognitive.IdentifyCategorize.Unspecified': ['identified object', 'identified role', 'identifier', 'place'], 'Cognitive.Inspection.SensoryObserve': ['instrument', 'observed entity', 'observer', 'place'], 'Cognitive.Research.Unspecified': ['place', 'researcher', 'subject'], 'Cognitive.TeachingTrainingLearning.Unspecified': ['learner', 'teacher trainer'], 
                                           'Conflict.Attack.DetonateExplode': ['attacker', 'explosive device', 'instrument', 'place', 'target'], 'Conflict.Attack.Unspecified': ['attacker', 'instrument', 'place', 'target'], 'Conflict.Defeat.Unspecified': ['defeated', 'place', 'victor'], 'Conflict.Demonstrate.DemonstrateWithViolence': ['demonstrator', 'regulator'], 'Conflict.Demonstrate.Unspecified': ['demonstrator', 'target', 'topic'], 
                                           'Contact.Contact.Broadcast': ['communicator', 'instrument', 'place', 'recipient', 'topic'], 'Contact.Contact.Correspondence': ['participant', 'place', 'topic'], 'Contact.Contact.Meet': ['participant', 'place', 'topic'], 'Contact.Contact.Unspecified': ['participant', 'place', 'topic'], 'Contact.RequestCommand.Broadcast': ['communicator', 'recipient'], 
                                           'Contact.RequestCommand.Correspondence': ['communicator', 'recipient', 'topic'], 'Contact.RequestCommand.Meet': ['communicator', 'recipient'], 'Contact.RequestCommand.Unspecified': ['communicator', 'place', 'recipient'], 'Contact.ThreatenCoerce.Broadcast': ['communicator', 'recipient'], 'Contact.ThreatenCoerce.Correspondence': ['communicator', 'recipient'], 
                                           'Contact.ThreatenCoerce.Unspecified': ['communicator', 'recipient'], 'Control.ImpedeInterfereWith.Unspecified': ['impeder', 'place'], 'Disaster.Crash.Unspecified': ['crash object', 'place', 'vehicle'], 'Disaster.DiseaseOutbreak.Unspecified': ['disease', 'place', 'victim'], 'GenericCrime.GenericCrime.GenericCrime': ['perpetrator', 'place', 'victim'], 'Justice.Acquit.Unspecified': ['defendant'], 
                                           'Justice.ArrestJailDetain.Unspecified': ['detainee', 'jailer', 'place'], 'Justice.ChargeIndict.Unspecified': ['defendant', 'judge court', 'place', 'prosecutor'], 'Justice.Convict.Unspecified': ['defendant', 'judge court'], 'Justice.InvestigateCrime.Unspecified': ['defendant', 'investigator', 'observed entity', 'observer', 'place'], 'Justice.ReleaseParole.Unspecified': ['defendant', 'judge court'], 
                                           'Justice.Sentence.Unspecified': ['defendant', 'judge court', 'place'], 'Justice.TrialHearing.Unspecified': ['defendant', 'judge court', 'place', 'prosecutor'], 'Life.Die.Unspecified': ['killer', 'place', 'victim'], 'Life.Infect.Unspecified': ['victim'], 'Life.Injure.Unspecified': ['body part', 'injurer', 'instrument', 'victim'], 'Medical.Intervention.Unspecified': ['patient', 'place', 'treater'], 
                                           'Movement.Transportation.Evacuation': ['destination', 'origin', 'passenger artifact', 'transporter'], 'Movement.Transportation.IllegalTransportation': ['destination', 'passenger artifact', 'transporter', 'vehicle'], 'Movement.Transportation.PreventPassage': ['destination', 'origin', 'passenger artifact', 'preventer', 'transporter', 'vehicle'], 
                                           'Movement.Transportation.Unspecified': ['destination', 'origin', 'passenger artifact', 'transporter', 'vehicle'], 'Personnel.EndPosition.Unspecified': ['employee', 'place of employment'], 'Personnel.StartPosition.Unspecified': ['employee', 'place', 'place of employment', 'position'], 'Transaction.Donation.Unspecified': ['artifact money', 'giver', 'recipient'], 
                                           'Transaction.ExchangeBuySell.Unspecified': ['acquired entity', 'giver', 'payment barter', 'recipient']}
wikievent_event_description_dict = {
    "ArtifactExistence.DamageDestroyDisableDismantle.Damage": "damager ( and damager ) damaged artifact ( and artifact ) using instrument ( and instrument ) in place ( and place )",
    "ArtifactExistence.DamageDestroyDisableDismantle.Destroy": "destroyer ( and destroyer ) destroyed artifact ( and artifact ) using instrument ( and instrument ) in place ( and place )",
    "ArtifactExistence.DamageDestroyDisableDismantle.DisableDefuse": "disabler ( and disabler ) disabled or defused artifact ( and artifact ) using instrument ( and instrument ) in place ( and place )",
    "ArtifactExistence.DamageDestroyDisableDismantle.Dismantle": "dismantler ( and dismantler ) dismantled artifact ( and artifact ) using instrument ( and instrument ) from components ( and components ) in place ( and place )",
    "ArtifactExistence.DamageDestroyDisableDismantle.Unspecified": "damager destroyer ( and damager destroyer ) damaged or destroyed artifact ( and artifact ) using instrument ( and instrument ) in place ( and place )",
    "ArtifactExistence.ManufactureAssemble.Unspecified": "manufacturer assembler ( and manufacturer assembler ) manufactured or assembled or produced artifact ( and artifact ) from components ( and components ) using instrument ( and instrument ) at place ( and place )",
    "Cognitive.IdentifyCategorize.Unspecified": "identifier ( and identifier ) identified identified object ( and identified object ) as identified role ( and identified role ) at place ( and place )",
    "Cognitive.Inspection.SensoryObserve": "observer ( and observer ) observed observed entity ( and observed entity ) using instrument ( and instrument ) in place ( and place )", 
    "Cognitive.Research.Unspecified": "researcher ( and researcher ) researched subject ( and subject ) using Means ( and Means ) at place ( and place )",
    "Cognitive.TeachingTrainingLearning.Unspecified": "teacher trainer ( and teacher trainer ) taught FieldOfKnowledge ( and FieldOfKnowledge ) to learner ( and learner ) using Means ( and Means ) at Institution ( and Institution ) in place ( and place )",
    "Conflict.Attack.DetonateExplode": "attacker ( and attacker ) detonated or exploded explosive device ( and explosive device ) using instrument ( and instrument ) to attack target ( and target ) at place ( and place )",
    "Conflict.Attack.Unspecified": "attacker ( and attacker ) attacked target ( and target ) using instrument ( and instrument ) at place ( and place )",
    "Conflict.Defeat.Unspecified": "victor ( and victor ) defeated in ConflictOrElection at place ( and place )",
    "Conflict.Demonstrate.DemonstrateWithViolence": "demonstrator ( and demonstrator ) was in a demonstration involving violence for topic ( and topic ) with VisualDisplay against target ( and target ) at place ( and place ), with potential involvement of regulator police or military",
    "Conflict.Demonstrate.Unspecified": "demonstrator ( and demonstrator ) was in a demonstration for topic ( and topic ) with VisualDisplay against target ( and target ) at place ( and place ), with potential involvement of regulator police or military",
    "Contact.Contact.Broadcast": "communicator ( and communicator ) communicated to recipient ( and recipient ) about topic ( and topic ) using instrument ( and instrument ) at place ( and place ) (one-way communication)",
    "Contact.Contact.Correspondence": "participant ( and participant ) communicated remotely with participant ( and participant ) about topic ( and topic ) using instrument ( and instrument ) at place ( and place )",
    "Contact.Contact.Meet": "participant ( and participant ) met face-to-face with participant ( and participant ) about topic ( and topic ) at place ( and place )",
    "Contact.Contact.Unspecified": "participant ( and participant ) communicated with participant ( and participant ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.Prevarication.Unspecified": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.RequestCommand.Unspecified": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.RequestCommand.Broadcast": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.RequestCommand.Correspondence": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.RequestCommand.Meet": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.ThreatenCoerce.Unspecified": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.ThreatenCoerce.Broadcast": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Contact.ThreatenCoerce.Correspondence": "communicator ( and communicator ) communicated with recipient ( and recipient ) about topic ( and topic ) at place ( and place ) (document does not specify in person or not, or one-way or not)",
    "Control.ImpedeInterfereWith.Unspecified": "impeder ( and impeder ) impeded or interfered with ImpededEvent at place ( and place )",
    "Disaster.Crash.Unspecified": "DriverPassenger in vehicle ( and vehicle ) crashed into crash object ( and crash object ) at place ( and place )",
    "Disaster.DiseaseOutbreak.Unspecified": "disease ( and disease ) broke out among victim ( and victim ) or population at place ( and place )",
    "Disaster.FireExplosion.Unspecified": "FireExplosionObject caught fire or exploded from instrument ( and instrument ) at place ( and place )",
    "GenericCrime.GenericCrime.GenericCrime": "perpetrator committed a crime against victim ( and victim ) at place ( and place )",
    "Justice.Acquit.Unspecified": "judge court acquitted defendant ( and defendant ) of Crime ( and Crime ) in place ( and place )",
    "Justice.ArrestJailDetain.Unspecified": "jailer arrested or jailed detainee for Crime ( and Crime ) at place ( and place )",
    "Justice.ChargeIndict.Unspecified": "prosecutor charged or indicted defendant ( and defendant ) before judge court for Crime ( and Crime ) in place ( and place )",
    "Justice.Convict.Unspecified": "judge court convicted defendant ( and defendant ) of Crime ( and Crime ) in place ( and place )",
    "Justice.InvestigateCrime.Unspecified": "investigator investigated defendant ( and defendant ) for Crime ( and Crime ) in place ( and place )",
    "Justice.ReleaseParole.Unspecified": "judge court released or paroled defendant ( and defendant ) from Crime ( and Crime ) in place ( and place )",
    "Justice.Sentence.Unspecified": "judge court sentenced defendant ( and defendant ) for Crime ( and Crime ) to Sentence in place ( and place )",
    "Justice.TrialHearing.Unspecified": "prosecutor tried defendant ( and defendant ) before judge court for Crime ( and Crime ) in place ( and place )",
    "Life.Consume.Unspecified": "ConsumingEntity consumed ConsumedThing at place ( and place )",
    "Life.Die.Unspecified": "victim ( and victim ) died at place ( and place ) from MedicalIssue, killed by killer",
    "Life.Illness.Unspecified": "victim ( and victim ) has disease ( and disease ) sickness or illness at place ( and place ), deliberately infected by DeliberateInjurer",
    "Life.Infect.Unspecified": "victim ( and victim ) was infected with InfectingAgent from Source at place ( and place )",
    "Life.Injure.Unspecified": "victim ( and victim ) was injured by injurer using instrument ( and instrument ) in body part with MedicalCondition at place ( and place )",        
    "Medical.Diagnosis.Unspecified": "treater diagnosed patient with SymptomSign for MedicalCondition at place ( and place )",
    "Medical.Intervention.Unspecified": "treater treated patient for MedicalIssue with instrument ( and instrument ) Means ( and Means ) at place ( and place )",
    "Medical.Vaccinate.Unspecified": "treater vaccinated patient via VaccineMethod for VaccineTarget at place ( and place )",
    "Movement.Transportation.Evacuation": "transporter transported passenger artifact in vehicle ( and vehicle ) from origin place ( and origin place ) to destination place ( and destination place )",
    "Movement.Transportation.IllegalTransportation": "transporter illegally transported passenger artifact in vehicle ( and vehicle ) from origin place ( and origin place ) to destination place ( and destination place )",
    "Movement.Transportation.PreventPassage": "preventer prevents transporter from entering destination place ( and destination place ) from origin place ( and origin place ) to transport passenger artifact using vehicle ( and vehicle )",
    "Movement.Transportation.Unspecified": "transporter transported passenger artifact in vehicle ( and vehicle ) from origin place ( and origin place ) to destination place ( and destination place )",
    "Personnel.EndPosition.Unspecified": "employee stopped working in position at place of employment organization in place ( and place )",
    "Personnel.StartPosition.Unspecified": "employee started working in position at place of employment organization in place ( and place )",
    "Transaction.Donation.Unspecified": "giver gave artifact money to recipient ( and recipient ) for the benefit of Beneficiary ( and Beneficiary ) at place ( and place )",       
    "Transaction.ExchangeBuySell.Unspecified": "giver bought, sold, or traded acquired entity to recipient ( and recipient ) in exchange for payment barter for the benefit of Beneficiary ( and Beneficiary ) at place ( and place )"
}


try:
    with open("force_tokens.json", 'r') as f:
        force_tokens = json.load(f)
except:
    print("目前还没有force_tokens.json文件！！！")


cate_list = {
    "ACE05_EN_EAE": ACE05_argument_role_list,
    "ACE05_EN_EAE_one": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_test": ACE05_argument_role_list,
    "ACE05_EN_EAE_local_context_one_no_empty_role": ACE05_argument_role_list,
    "ACE05_EN_EAE_local_context_one_no_empty_role_test": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_005": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_010": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_020": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_030": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_050": ACE05_argument_role_list,        
    "ACE05_EN_EAE_one_no_empty_role_075": ACE05_argument_role_list, 
    "ere_en_eae_one_no_empty_role": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_001": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_002": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_003": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_005": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_010": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_020": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_030": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_050": ere_argument_role_list, 
    "wikievent-mvp-eae-one-no-empty": wikievent_argument_role_list,
    "wikievent-mvp-eae-one-no-empty-role": wikievent_argument_role_list,
    "wikievent-mvp-eae-one-no-empty-role-test": wikievent_argument_role_list,      
}

cate_list_eae = {
    "ACE05_EN_EAE": ACE05_argument_role_list,
    "ACE05_EN_EAE_one": ACE05_argument_role_list,   
    "ACE05_EN_EAE_one_no_empty": ACE05_argument_role_list, 
    "ACE05_EN_EAE_one_no_empty_role": ACE05_argument_role_list, 
    "ACE05_EN_EAE_one_no_empty_role_test": ACE05_argument_role_list, 
    "ACE05_EN_EAE_local_context_one_no_empty_role": ACE05_argument_role_list, 
    "ACE05_EN_EAE_local_context_one_no_empty_role_test": ACE05_argument_role_list, 
    "ACE05_EN_EAE_one_no_empty_role_005": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_010": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_020": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_030": ACE05_argument_role_list,
    "ACE05_EN_EAE_one_no_empty_role_050": ACE05_argument_role_list,        
    "ACE05_EN_EAE_one_no_empty_role_075": ACE05_argument_role_list,  
    "ere_en_eae_one_no_empty_role": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_001": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_002": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_003": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_005": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_010": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_020": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_030": ere_argument_role_list, 
    "ere_en_eae_one_no_empty_role_050": ere_argument_role_list,       
    "wikievent-mvp-eae-one-no-empty": wikievent_argument_role_list,      
    "wikievent-mvp-eae-one-no-empty-role": wikievent_argument_role_list,      
    "wikievent-mvp-eae-one-no-empty-role-test": wikievent_argument_role_list,      
}

task_data_list = {
    'ae': ['laptop14', 'rest14', 'rest15'],
    'alsc': ['laptop14', 'rest14', 'rest15'],
    'oe': ['laptop14', 'rest14', 'rest15'],
    'aoe': ['laptop14', 'rest14', 'rest15', 'rest16'],
    "aste": ["laptop14", "rest14", "rest15", "rest16"],
    "tasd": ['rest15', "rest16"],
    "acos": ['laptop16', "rest16"],
    "asqp": ['rest15', "rest16"],
    "eae": ["ACE05_EN_EAE", "ACE05_EN_EAE_one", "ACE05_EN_EAE_one_no_empty", "ACE05_EN_EAE_one_no_empty_role", "ACE05_EN_EAE_one_no_empty_role_test",
            "ACE05_EN_EAE_local_context_one_no_empty_role", "ACE05_EN_EAE_local_context_one_no_empty_role_test",  
            "ACE05_EN_EAE_one_no_empty_role_001", "ACE05_EN_EAE_one_no_empty_role_002", "ACE05_EN_EAE_one_no_empty_role_003",             
            "ACE05_EN_EAE_one_no_empty_role_005", "ACE05_EN_EAE_one_no_empty_role_010", "ACE05_EN_EAE_one_no_empty_role_020", 
            "ACE05_EN_EAE_one_no_empty_role_030", "ACE05_EN_EAE_one_no_empty_role_050", "ACE05_EN_EAE_one_no_empty_role_075",
            "ere_en_eae_one_no_empty_role", "ere_en_eae_one_no_empty_role_001", "ere_en_eae_one_no_empty_role_002",
            "ere_en_eae_one_no_empty_role_003", "ere_en_eae_one_no_empty_role_005", "ere_en_eae_one_no_empty_role_010",
            "ere_en_eae_one_no_empty_role_020", "ere_en_eae_one_no_empty_role_030", "ere_en_eae_one_no_empty_role_050",    
            "wikievent-mvp-eae-one-no-empty", "wikievent-mvp-eae-one-no-empty-role", "wikievent-mvp-eae-one-no-empty-role-test"]
}


force_words = {
    'aste': {
        'rest15': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest16': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest14': list(senttag2opinion.values()) + ['[SSEP]'],
        'laptop14': list(senttag2opinion.values()) + ['[SSEP]']
    },
    'ae': {
        'rest15': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest14': list(senttag2opinion.values()) + ['[SSEP]'],
        'laptop14': list(senttag2opinion.values()) + ['[SSEP]']
    },
    'alsc': {
        'rest15': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest14': list(senttag2opinion.values()) + ['[SSEP]'],
        'laptop14': list(senttag2opinion.values()) + ['[SSEP]']
    },    
    'oe': {
        'rest15': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest14': list(senttag2opinion.values()) + ['[SSEP]'],
        'laptop14': list(senttag2opinion.values()) + ['[SSEP]']
    },    
    'aoe': {
        'rest15': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest16': list(senttag2opinion.values()) + ['[SSEP]'],
        'rest14': list(senttag2opinion.values()) + ['[SSEP]'],
        'laptop14': list(senttag2opinion.values()) + ['[SSEP]']
    },

}

force_words_eae = {
    'eae': {
        'ACE05_EN_EAE': ACE05_argument_role_list,
        'ACE05_EN_EAE_one': ACE05_argument_role_list,
        'ACE05_EN_EAE_one_no_empty': ACE05_argument_role_list,
        'ACE05_EN_EAE_one_no_empty_role': ACE05_argument_role_list,
        'ACE05_EN_EAE_one_no_empty_role_test': ACE05_argument_role_list,
        'ACE05_EN_EAE_local_context_one_no_empty_role': ACE05_argument_role_list,
        'ACE05_EN_EAE_local_context_one_no_empty_role_test': ACE05_argument_role_list,
        "ACE05_EN_EAE_one_no_empty_role_005": ACE05_argument_role_list,
        "ACE05_EN_EAE_one_no_empty_role_010": ACE05_argument_role_list,
        "ACE05_EN_EAE_one_no_empty_role_020": ACE05_argument_role_list,
        "ACE05_EN_EAE_one_no_empty_role_030": ACE05_argument_role_list,
        "ACE05_EN_EAE_one_no_empty_role_050": ACE05_argument_role_list,        
        "ACE05_EN_EAE_one_no_empty_role_075": ACE05_argument_role_list,  
        "ere_en_eae_one_no_empty_role": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_001": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_002": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_003": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_005": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_010": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_020": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_030": ere_argument_role_list, 
        "ere_en_eae_one_no_empty_role_050": ere_argument_role_list,               
        "wikievent-mvp-eae-one-no-empty": wikievent_argument_role_list,         
        "wikievent-mvp-eae-one-no-empty-role": wikievent_argument_role_list,         
        "wikievent-mvp-eae-one-no-empty-role-test": wikievent_argument_role_list,         
    }
}

optim_orders_all_eae = {
    "eae": {
        "ACE05_EN_EAE": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],
        "ACE05_EN_EAE_one": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],
        "ACE05_EN_EAE_one_no_empty": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],      
        "ACE05_EN_EAE_one_no_empty_role": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],              
        "ACE05_EN_EAE_one_no_empty_role_test": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],           
        "ACE05_EN_EAE_local_context_one_no_empty_role": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],              
        "ACE05_EN_EAE_local_context_one_no_empty_role_test": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],           
        "ACE05_EN_EAE_one_no_empty_role_001": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],             
        "ACE05_EN_EAE_one_no_empty_role_002": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],             
        "ACE05_EN_EAE_one_no_empty_role_003": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],             
        "ACE05_EN_EAE_one_no_empty_role_005": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],        
        "ACE05_EN_EAE_one_no_empty_role_010": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],     
        "ACE05_EN_EAE_one_no_empty_role_020": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],        
        "ACE05_EN_EAE_one_no_empty_role_030": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],   
        "ACE05_EN_EAE_one_no_empty_role_050": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_001": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_002": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_003": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_005": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_010": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_020": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_030": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "ere_en_eae_one_no_empty_role_050": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ], 
        "wikievent-mvp-eae-one-no-empty": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],
        "wikievent-mvp-eae-one-no-empty-role": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ],
        "wikievent-mvp-eae-one-no-empty-role-test": [
            '[T] [A] [R]', '[T] [R] [A]',
            '[A] [R] [T]', '[R] [A] [T]'
        ]                                                        
    }
}



heuristic_orders = {
    'ae': ['[A]'],
    'alsc': ['[A] [S]'],
    'oe': ['[O]'],
    'aoe': ['[O]'], 
    'aste': ['[A] [O] [S]'],
    'tasd': ['[A] [C] [S]'],
    'asqp': ['[A] [O] [C] [S]'],
    'acos': ['[A] [O] [C] [S]'],
    'eae': ['[T] [A] [R]']
}