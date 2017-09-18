from classes import Attorney

def getListOfAttorneys():

    listOfAttorneys = list()

    # Attorney Names are listed in all Caps on PDFs.  Put names in as
    # full caps for an exact match.  This may no longer be necessary after
    # recent changes, but I am continuing to do it for now.

    atty3 = Attorney("NORRIS, JON W", "test@fakeemail.com")
    listOfAttorneys.append(atty3)

    atty4 = attorney("KEY, THOMAS A", 'test@fakeemail.com')
    listOfAttorneys.append(atty4)

    atty5 = Attorney("PUTTAGUNTA, RUPA R", 'test@fakeemail.com')
    listOfAttorneys.append(atty5)

    atty6 = attorney("ENGLE, THOMAS D", 'test@fakeemail.com')
    listOfAttorneys.append(atty6)

    atty7 = attorney("WINTERS, DOMINIQUE D", 'test@fakeemail.com')
    listOfAttorneys.append(atty7)

    attorneyOne = Attorney("CLENNON, CARY", "test@fakeemail.com")
    listOfAttorneys.append(attorneyOne)
    
    return listOfAttorneys