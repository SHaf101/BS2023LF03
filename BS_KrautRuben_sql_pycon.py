import mysql.connector
import datetime

LOGIN = 1
LOGINHELP = """
    login user [email]
    login admin [password]
---------------------------------"""

USER = 2
USERHELP = """
    profile info
    profile delete
    order [recipe_nr]           TD
    logout
---------------------------------
"""

ADMIN = 4
ADMINHELP = """
    create category [name]
    create label [name]
    logout
---------------------------------
"""

ANYHELP = """
--------HELP---------------------
    create recipe               
    show recipes                
    show recipes all            
    show ingredients [recipe name]          
    show ingredients
    show ingredients notused
    show categories
    show labels
    exit
"""

CREATERECIPEHELP="""
create Recipe help:
Name:       [Name of recipe]
Kategorien: [Category number 1] [Category number 2] ...
Zutaten:    [Ingredient 1] [Amount] [Ingredient 2] [Amount] ...
"""

QUERYRECIPEHELP="""
query Recipe help:
Options:    [option 1] [option 2] ... (inclcat, incllabel, exlabel, inclingredients, exingredients)
Categories: [Cat Nr1] [Cat Nr 2] ...
Include Labels: [Label Nr 1] ...
Exclude Labels: [Label Nr 1] ...
Incl. Ingredients: [Ingredient Nr 1] ...
Excl. Ingredients: [Ingredient Nr 1] ...
"""

class Main:

    def __init__(self) -> None:
        self.status = 1
        self.oplevel = LOGIN
        self.user = 1
        self.db = mysql.connector.connect(user='user', password='user1234', host='h2970290.stratoserver.net', db='krautundrueben')
        print(self.db.get_server_info())
        print(self.db.get_server_version())
        self.cursor = self.db.cursor()
        self.record = []
        self.sqlresult = []
        pass
    
    def main(self):
        print("Welcome!")
        while self.status == 1:
            userinput = input()
            coutput = self.command(userinput)
            print(coutput)
            pass
        pass

    def getRecord(self, sqlquery):
        self.cursor.execute(sqlquery)
        self.record = self.cursor.fetchall()
        pass
    
    def command(self, string:str):
        string = string.lower()
        strc = string.split()
        if(len(strc)<1):
            return self.returnHelp()
            pass

        if strc[0] == "exit" and len(strc)==1:
            self.status = 0
            return "Exit successful. Bye!"
            pass
        '''
        login user [email]      OK
        login admin [password]  OK  
        logout                  OK
        '''
        if strc[0] == "login" and self.oplevel==LOGIN and len(strc)>= 3:
            if self.loginAs(strc[1:]):
                return "Login successful"
                pass
            else:
                return "Login unsuccessful"
                pass
            pass
        if strc[0] == "logout" and self.oplevel!=LOGIN:
            self.logout()
            return "Logout successful"
            pass
        '''
        create recipe (name, categories, ingredients)   OK
        create category [name]                          OK
        create label [name]                             OK
        '''
        if strc[0] == "create":
            if strc[1] == "recipe":
                if self.createRecipe():
                    return "Recipe created!"
                else:
                    return "Recipe could not be created!"
                pass
            if strc[1] == "category" and self.oplevel==ADMIN:
                if self.createCategory(strc[2]):
                    return f"Category {strc[2]} created!"
                else:
                    return "Category could not be created..."
                pass
            if strc[1] == "label" and self.oplevel==ADMIN:
                if self.createLabel(strc[2]):
                    return f"Label {strc[2]} created!"
                else:
                    return "Label could not be created!"
                pass
            pass

        '''
        show recipes (categories, include label, exclude label)         TESTING
        show recipes all                                                OK
        show ingredients [recipe name]                                  OK
        show ingredients                                                OK
        show ingredients notused                                        OK
        show categories                                                 OK
        show labels                                                     OK
        '''
        if strc[0] == "show":
            #showRecipe() funkt noicht
            if strc[1] == "recipes":
                if len(strc) == 3 and strc[2] == "all":
                    if self.showRecipesAll():
                        print(self.sqlresult)
                        return ""
                        return True
                    pass
                elif len(strc) == 2:
                    if self.showRecipe():
                        print(self.sqlresult)
                        return ""
                    pass
                return False
                pass
            if strc[1] == "ingredients":
                if len(strc) == 3 and strc[2] == "notused":
                    if self.showIngredientsNotUsed():
                        print("\nAlle Zutaten die in keinem Rezept verwendet werden: ")
                        print(self.sqlresult)
                        return ""
                    pass
                elif len(strc) >= 3:
                    if self.showRecipeIngredients(" ".join(strc[2:])):
                        print(self.sqlresult)
                        return ""
                    pass
                else:
                    if self.showIngredients():
                        print("\nAlle Zutaten: ")
                        print(self.sqlresult)
                        return ""
                        pass
                pass
            if len(strc) >= 3 and strc[1] == "recipe":
                if self.showRecipeIngredients(" ".join(strc[2:])):
                    print(self.sqlresult)
                    return ""
                    pass
                pass
            if strc[1] == "categories":
                if self.showCategories():
                    print("\nAlle Kategorien: ")
                    print(self.sqlresult)
                    return ""
                    pass
                pass
            if strc[1] == "labels":
                self.showLabels()
                print(self.sqlresult)
                return ""
                pass
            pass

        '''
        profile info            OK 
        profile delete          OK
        '''
        if strc[0] == "profile" and self.oplevel==USER:
            if strc[1] == "info":
                if self.userInfo():
                    #print(self.sqlresult)
                    return f"""
        Kundennr:   {self.sqlresult[0][0]}
        Name:       {self.sqlresult[0][2]} {self.sqlresult[0][1]}
        Geburtstag: {self.sqlresult[0][3]}
        Adresse:    {self.sqlresult[0][4]} {self.sqlresult[0][5]} {self.sqlresult[0][6]} {self.sqlresult[0][7]}
        Telefon:    {self.sqlresult[0][8]}
        E-Mail:     {self.sqlresult[0][9]}
        Durchschnittliche Kalorien pro Bestellung: {self.sqlresult[2][0]}
        Gesamte Kalorien aller Bestellungen: {self.sqlresult[1][0]}"""
                    pass
                pass
            if strc[1] == "delete":
                if self.userDelete():
                    self.oplevel = LOGIN
                    return "User deleted!"
                else:
                    return "User NOT deleted!"
                pass
            pass
        '''
        order       P
        help        OK
        '''
        if strc[0] == "order" and self.oplevel==USER and len(strc) == 2:
            if self.order(strc[1]):
                return ""
            else:
                return "Order could not be created... Sorry!"
            pass
        #OK
        if strc[0] == "help":
            return self.returnHelp()
        #------------------------------------
        return "Enter >help< for help."
        pass

    def loginAs(self, strc:str):
        if strc[0] == "user":
            if not self.sqlcommand(f"Select KUNDENNR from KUNDE Where Email='{strc[1]}'") or len(self.sqlresult) == 0:
                return False
            if self.sqlresult[0][0] < 10:
                return False
            self.oplevel = USER
            self.user = self.sqlresult[0][0]
            return True
            pass
        elif strc[0] == "admin":
            if strc[1] == 'secretpassword':
                self.oplevel = ADMIN
                self.user = 0
                return True
            return False
        pass
    
    def logout(self):
        self.oplevel = LOGIN
        self.user = 1
        return True
        pass

    def createRecipe(self):
        print(CREATERECIPEHELP)
        status = 0
        rezeptname = input("Name: ")
        kategorien = input("Kategorien: ")
        kategorien = kategorien.split()
        zutaten = input("Zutaten: ")
        zutaten = zutaten.split()
        if(len(zutaten)%2!=0):
            return False

        if not self.sqlcommand(f"""
INSERT INTO REZEPT (REZEPT.REZEPTNAME, REZEPT.KUNDENNR)
VALUES ('{rezeptname}', '{self.user}'); 
""", type="chnoco"):
            status = status+1

        if not self.sqlcommand(f"""
SELECT REZEPTNR FROM REZEPT
WHERE REZEPT.REZEPTNR = LAST_INSERT_ID();
"""):
            status = status+1

        rezeptid = self.sqlresult[0][0]

        for kat in kategorien:
            if not self.sqlcommand(f"""
INSERT INTO REZEPTKATEGORIEN (REZEPTKATEGORIEN.REZEPTNR, REZEPTKATEGORIEN.KATEGORIENR)
VALUES ('{rezeptid}', '{kat}');
""", type="chnoco"):
                status = status+1
            pass

        for i in range(0,len(zutaten),2):
            if not self.sqlcommand(f"""
INSERT INTO REZEPTZUTATEN (REZEPTZUTATEN.REZEPTNR, REZEPTZUTATEN.ZUTATENNR, REZEPTZUTATEN.MENGE)
VALUES ('{rezeptid}', '{zutaten[i]}', '{zutaten[i+1]}');
""", type="chnoco"):
                status = status+1
            pass
        
        if status == 0:
            self.db.commit()
            return True
        else:
            self.db.rollback()
            return False
        pass

    def createLabel(self, strc:str):
        labelname = strc.capitalize()
        return self.sqlcommand(f"INSERT INTO LABEL (BEZEICHNUNG) VALUES ('{labelname}');", type="change")
        pass

    def createCategory(self, strc:str):
        categoryname = strc.capitalize()
        return self.sqlcommand(f"INSERT INTO KATEGORIEN (BEZEICHNUNG) VALUES ('{categoryname}');", type="change")
        pass

    def showLabels(self):
        return self.sqlcommand("SELECT BEZEICHNUNG, LABELNR FROM LABEL;")
        pass

    def showRecipe(self):
        """
        query Recipe help:
        Options:    [option 1] [option 2] ... (inclcat, incllabel, exlabel, inclingredients, exingredients)
        Categories: [Cat Nr1] [Cat Nr 2] ...
        Include Labels: [Label Nr 1] ...
        Exclude Labels: [Label Nr 1] ...
        Incl. Ingredients: [Ingredient Nr 1] ...
        Excl. Ingredients: [Ingredient Nr 1] ...
        """

        print(QUERYRECIPEHELP)
        options = input("Options: ")
        options = options.lower().split()

        category = input("Categories: ")
        category = category.split()
        category = "'" + "','".join(category) + "'"

        yeslabel = input("Include Labels: ")
        yeslabel = yeslabel.split()
        yeslabel = "'" + "','".join(yeslabel) + "'"

        nolabel = input("Exclude Labels: ")
        nolabel = nolabel.split()
        nolabel = "'" + "','".join(nolabel) + "'"

        yesingr = input("Include Ingredients: ")
        yesingr = yesingr.split()
        yesingr = "'" + "','".join(yesingr) + "'"

        noingr = input("Exclude Ingredients: ")
        noingr = noingr.split()
        noingr = "'" + "','".join(noingr) + "'"
#------------------------------------------------------------------------
        sqlexcllabel = f"""
AND REZEPT.REZEPTNR NOT IN
	(
		SELECT REZEPTZUTATEN.REZEPTNR
		FROM
		(
			REZEPTZUTATEN INNER JOIN ZUTATLABEL ON REZEPTZUTATEN.ZUTATENNR=ZUTATLABEL.ZUTATENNR
		)
		WHERE LABELNR IN ({nolabel})
	)
"""
        if not "exlabel" in options:
            sqlexcllabel = ""
            pass

        sqlincllabel = f"""
AND REZEPT.REZEPTNR IN
	(
		SELECT REZEPTZUTATEN.REZEPTNR
		FROM
		(
			REZEPTZUTATEN INNER JOIN ZUTATLABEL ON REZEPTZUTATEN.ZUTATENNR=ZUTATLABEL.ZUTATENNR
		)
		WHERE LABELNR IN ({yeslabel})
	)
"""
        if not "incllabel" in options:
            sqlincllabel = ""
            pass

        sqlincling = f"""
AND REZEPTZUTATEN.ZUTATENNR IN ({yesingr})
"""
        if not "inclingredients" in options:
            sqlincling = ""
            pass

        sqlexcling = f"""
AND REZEPTZUTATEN.ZUTATENNR NOT IN ({noingr})
"""
        if not "exingredients" in options:
            print("no exingredients")
            sqlexcling = ""
            pass

        sqlinclcat = f"""
AND REZEPTKATEGORIEN.KATEGORIENR IN ({category}) 
"""
        if not "inclcat" in options:
            print("No inclcat")
            sqlinclcat = ""
            pass

        sqlc = f"""
(
	SELECT DISTINCT REZEPT.REZEPTNR, REZEPT.REZEPTNAME
	FROM
	(
		(
			(
				REZEPT INNER JOIN REZEPTKATEGORIEN ON REZEPT.REZEPTNR=REZEPTKATEGORIEN.REZEPTNR
			)
			INNER JOIN KATEGORIEN ON REZEPTKATEGORIEN.KATEGORIENR=KATEGORIEN.KATEGORIENR
		)
		INNER JOIN REZEPTZUTATEN ON REZEPT.REZEPTNR=REZEPTZUTATEN.REZEPTNR
	)
    WHERE REZEPT.REZEPTNR > '-555'
	{sqlinclcat}
	{sqlincling}
	{sqlexcling}
	{sqlexcllabel}
	{sqlincllabel}
);
"""
#------------------------------------------------------------------------
        #sql command
        if self.sqlcommand(sqlc):
            return True
        else:
            return False
        pass

    def showRecipesAll(self):
        return self.sqlcommand("SELECT REZEPT.REZEPTNR, REZEPT.REZEPTNAME FROM REZEPT;")
        pass

    def showRecipeIngredients(self, recipename:str):
        return self.sqlcommand(f"""
SELECT REZEPTZUTATEN.ZUTATENNR, ZUTAT.BEZEICHNUNG, REZEPTZUTATEN.MENGE
FROM 
(
	(
		REZEPT INNER JOIN REZEPTZUTATEN ON REZEPT.REZEPTNR=REZEPTZUTATEN.REZEPTNR
	)
	INNER JOIN ZUTAT ON ZUTAT.ZUTATENNR=REZEPTZUTATEN.ZUTATENNR
)
WHERE REZEPT.REZEPTNAME='{recipename}'; """)
        pass

    def showIngredients(self):
        return self.sqlcommand("SELECT BEZEICHNUNG, ZUTATENNR, EINHEIT FROM ZUTAT;")
        pass

    def showIngredientsNotUsed(self):
        return self.sqlcommand(f"""
SELECT BEZEICHNUNG, ZUTATENNR
FROM ZUTAT
WHERE ZUTATENNR NOT IN 
(
	SELECT ZUTATENNR
	FROM REZEPTZUTATEN
); """)
        pass

    def showCategories(self):
        return self.sqlcommand("SELECT BEZEICHNUNG, KATEGORIENR FROM KATEGORIEN;")
        pass

    def userInfo(self):
        print(self.user)
        self.sqlcommand(f"""
SELECT SUM(a.KGESAMT) AS KALORIENGESAMT
FROM
(
	SELECT BESTELLUNG.BESTELLNR, BESTELLUNGZUTAT.ZUTATENNR, BESTELLUNGZUTAT.MENGE*ZUTAT.KALORIEN AS KGESAMT
	FROM((BESTELLUNG 
	INNER JOIN BESTELLUNGZUTAT ON BESTELLUNG.BESTELLNR=BESTELLUNGZUTAT.BESTELLNR)
	INNER JOIN ZUTAT ON BESTELLUNGZUTAT.ZUTATENNR=ZUTAT.ZUTATENNR)
	WHERE BESTELLUNG.KUNDENNR='{self.user}' 
) AS a;""")
        kgesamt = self.sqlresult
        self.sqlcommand(f"""
SELECT AVG(KSPB)
FROM
(
	SELECT BESTELLNR, SUM(KSUM) AS KSPB
	FROM
	(
		SELECT BESTELLUNG.BESTELLNR, BESTELLUNG.KUNDENNR, BESTELLUNGZUTAT.ZUTATENNR, ZUTAT.KALORIEN*BESTELLUNGZUTAT.MENGE AS KSUM
		FROM
		( 
			(
				BESTELLUNG INNER JOIN BESTELLUNGZUTAT ON BESTELLUNG.BESTELLNR=BESTELLUNGZUTAT.BESTELLNR
			)
			INNER JOIN ZUTAT ON ZUTAT.ZUTATENNR=BESTELLUNGZUTAT.ZUTATENNR
		)
		WHERE BESTELLUNG.KUNDENNR='{self.user}'
	) AS a
	GROUP BY BESTELLNR
) AS b;""")
        kavg = self.sqlresult
        self.sqlcommand(f"SELECT * FROM KUNDE WHERE KUNDENNR='{self.user}'")
        self.sqlresult= self.sqlresult + kgesamt + kavg
        print(self.sqlresult)
        return True
        pass

    def userDelete(self):
        if(input("Delete current User? [y/n]").lower() == 'y'):
            return self.sqlcommand(f"UPDATE KUNDE SET NACHNAME = 'OLD', VORNAME = 'OLD', GEBURTSDATUM = '{datetime.date(1900,1,1)}', STRASSE = 'OLD', HAUSNR = 'OLD', PLZ = 'OLD', ORT = 'OLD', TELEFON = 'OLD', EMAIL = '{self.user}@OLD' WHERE KUNDENNR = '{self.user}'", type="change")
            pass
        else:
            return False
            pass
        pass

    def order(self, strc:str):
        #sql command
        if False:
            return True
        else:
            return False
        pass

    def returnHelp(self):
        if self.oplevel == LOGIN:
            return ANYHELP + LOGINHELP
        if self.oplevel == USER:
            return ANYHELP + USERHELP
        if self.oplevel == ADMIN:
            return ANYHELP + ADMINHELP
        pass
    
    def sqlcommand(self, command:str, type="query"):
        self.cursor.execute(command)
        if type=="query":
            self.sqlresult = self.cursor.fetchall()
        if type=="change":
            self.db.commit()
        if type=="chnoco":
            pass
        return True

        try:
            pass
        except:
            print("FEHLER!")
            return False
            pass
        pass
    
    def sqlcommit(self):
        self.db.commit()
        pass
    pass


if __name__ == "__main__":
    m = Main()

    # m.user = 2001
    # m.userInfo()

    m.main()
    
    pass



