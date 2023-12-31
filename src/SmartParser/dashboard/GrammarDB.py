import sqlite3

class GrammarDB:
    def __init__(self, database_name="grammar.db"):
        self.database_name = database_name
        self.create_table()

    def create_table(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS GrammarDB (
        Section TEXT NOT NULL,
        RuleNumber INTEGER NOT NULL,
        FieldName TEXT NOT NULL,
        Necessity TEXT NOT NULL,
        PrecedeCharacter TEXT NOT NULL,
        Format TEXT NOT NULL,
        ValidatorType TEXT NOT NULL,
        LinkTo TEXT NOT NULL,
        PRIMARY KEY (Section, RuleNumber))''')
        conn.commit()
        conn.close()

    def insert_data(self, section, rn, field_name, necessity, precede_character, format1, validator_type, LinkTo):
        rule_number = int(rn)
        conn = self.create_connection()
        cursor = conn.cursor()


        cursor.execute('SELECT * FROM GrammarDB WHERE Section = ?', (section,))
        sec = cursor.fetchall()
        next_row = len(sec)+1
        insert_num = rule_number
        
        # # print(section, rule_number, field_name, necessity, precede_characer, format1, LinkTo)
        if rule_number in range(1,next_row):
            row = next_row-1
            while row >= rule_number:
                cursor.execute('UPDATE GrammarDB SET RuleNumber = ? WHERE Section = ? AND RuleNumber = ?', (row+1, section, row))
                row -= 1
        else:
            insert_num = next_row
        # If the row does not exist, simply insert it
        
        cursor.execute('''
            INSERT INTO GrammarDB (Section, RuleNumber, FieldName, Necessity, PrecedeCharacter, Format, ValidatorType, LinkTo)
            VALUES (?,?, ?, ?, ?, ?, ?,?)
            ''', (section, insert_num, field_name, necessity, precede_character, format1, validator_type, LinkTo))
        conn.commit()
        conn.close()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.database_name)
            return conn
        except sqlite3.Error as e:
            print(e)
            return None
        
    def get_all_rules(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        sections = ['HEADER', 'CARRIER', 'ULD', 'BLK']
        columns = ["Section", "RuleNumber","FieldName", "Necessity", "PrecedeCharacter", "Format", "ValidatorType", "LinkTo"]
        rules_list = [[],[],[],[]]
        for j in range(len(sections)):
            cursor.execute('SELECT * FROM GrammarDB WHERE Section = ? ORDER BY RuleNumber ASC', (sections[j],))
            rows = cursor.fetchall()
            for row in rows:
                rule_dict = {columns[i]: row[i] for i in range(len(columns))}
                rules_list[j].append(rule_dict) 
        conn.close()
            
        return rules_list

    
    def clear_table(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM GrammarDB
        ''')
        conn.commit()
        conn.close()

    def delete_data(self, section, rn, field_name, necessity, precede_character, format1, validator_type, LinkTo):
        conn = self.create_connection()
        cursor = conn.cursor()
        rule_number = int(rn)
        cursor.execute('SELECT * FROM GrammarDB WHERE Section = ?', (section,))
        up = len(cursor.fetchall())
        cursor.execute('''
            DELETE FROM GrammarDB
            WHERE Section = ? AND RuleNumber = ? AND FieldName = ? AND Necessity = ? AND PrecedeCharacter = ? AND Format = ? AND ValidatorType = ? AND LinkTo = ?
        ''', (section, rule_number,field_name, necessity, precede_character, format1, validator_type, LinkTo))

        for row in range(rule_number+1, up+1):
            cursor.execute('UPDATE GrammarDB SET RuleNumber = ? WHERE Section = ? AND RuleNumber = ?',
                           (row - 1, section, row))

        conn.commit()
        conn.close()

    def update_data(self, section, rule_number, field_name, necessity, precede_character, format1, validator_type, LinkTo):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM GrammarDB WHERE Section = ?', (section,))
        sec = cursor.fetchall()

        if int(rule_number) in range(1,len(sec)+1):
            cursor.execute('UPDATE GrammarDB SET FieldName = ?, Necessity = ?, PrecedeCharacter = ?, Format = ?, ValidatorType = ?, LinkTo = ? WHERE Section = ? AND RuleNumber = ?',
                           (field_name, necessity, precede_character, format1, validator_type, LinkTo, section, rule_number))

        else:
            print("No matching rule to update, number of rules:", len(sec), 'rule no.', rule_number)
        conn.commit()
        conn.close()

    def reinsert_default(self):
        grammar_db.clear_table()

        grammar_db.insert_data("HEADER", 1, "CPM","Mandatory" ,"None","CPM", "None", "None")
        carrier_fields = [
            (1, "AirlineDesignator","Mandatory", "None", "mm(a)", "Airline", "None"),
            (2, "FlightNumber","Mandatory", "None", "fff(f)(a)", "None", "None"),
            (3, "DepartureDate","Optional", "/", "ff", "Date", "None"),
            (4, "RegistrationNumber","Mandatory", ".", "mm(m)(m)(m)(m)(m)(m)(m)(m)", "Registration", "None"),
            (5, "DepartureStation","Mandatory", ".", "aaa", "Airport", "None"),
            (6, "ULD_configuration","Optional", ".", "m{1,12}", "None", "None")
        ]

        for field in carrier_fields:
            rule_number,field_name, necessity, precede_character, format1, validator_type, link_to = field
            grammar_db.insert_data("CARRIER",rule_number, field_name, necessity, precede_character, format1, validator_type, link_to)

        uld_fields = [
        (1, "ULDBayDesignation", "Mandatory", "-", "m(m)(m)", "Bay", "LoadCategory"),
            (2, "ULDTypeCode", "Optional", "/", "amm((fffff)mm(a))", "ULDType", "None"),
            (3, "UnloadingStation", "Mandatory", "/", "aam", "Airport", "None"),
            (4, "Weight", "Optional", "/", "f(f)(f)(f)(f)", "None", "None"),
            (5, "LoadCategory", "Mandatory", "/", "a(a)(f)", "LoadCategory", "Weight, LoadCategory"),
            (6, "VolumeCode", "Optional", "/", "f", "None", "None"),
            (7, "ContourCode", "Optional", ".", "aaa/mm", "None", "None"),
            (8, "IMP", "Optional", ".", "aaa(/f(f)(f))", "IMP", "IMP"),

        ]
        for field in uld_fields:
            rule_number,field_name, necessity, precede_character, format1, validator_type, link_to = field
            grammar_db.insert_data("ULD", rule_number, field_name, necessity, precede_character, format1, validator_type, link_to)

        blk_fields = [
            (1, "Compartment", "Mandatory", "-", "f(f)", "Bay", "LoadCategory"),
            (2, "Destination", "Mandatory", "/", "aam", "Airport", "None"),
            (3, "Weight", "Optional", "/", "f(f)(f)(f)", "None", "None"),
            (4, "LoadCategory", "Mandatory", "/", "a(a)(f)", "LoadCategory", "Weight, LoadCategory"),
            (5, "IMP", "Optional", ".", "aaa(/f(f)(f))", "IMP", "IMP"),
            (6, "NumPieces", "Optional", ".", "PCSn(n)(n)(n)", "None", "None"),
            (7, "AVI", "Optional", ".", "VRf", "None", "None")
        ]
        for field in blk_fields:
            rule_number,field_name, necessity, precede_character, format1, validator_type, link_to = field
            grammar_db.insert_data("BLK", rule_number, field_name, necessity, precede_character, format1, validator_type, link_to)

        print(grammar_db.get_all_rules(), "In grammar DB")


grammar_db = GrammarDB()
# grammar_db.create_connection()
# grammar_db.clear_table()
# grammar_db.create_table()
# grammar_db.reinsert_default()
# print(grammar_db.get_all_rules(), "In grammar database")