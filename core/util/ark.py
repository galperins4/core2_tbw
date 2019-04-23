import psycopg2

class ArkDB:
    def __init__(self, db, u, pw, pk):
        self.db=db
        self.user=u
        self.password=pw
        self.PublicKey=pk
    
    
    def open_connection(self):
        self.connection = psycopg2.connect(
            dbname = self.db,
            user = self.user,
            password= self.password,
            host='localhost',
            port='5432')
            
        self.cursor=self.connection.cursor()
    
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
    
    
    def blocks(self, i='no', val=1, h=None):
        
        #if i is yes, first run grab every block forged for history
        if i == 'yes':
            try:
                self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
                "height" FROM blocks WHERE "generator_public_key" = '{self.PublicKey}' ORDER BY "height" DESC""")
                return self.cursor.fetchall()
            except Exception as e:
                print(e)

        # interval check to audit webhook for missing blocks
        elif i == 'interval':
            try:
                self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
                "height" FROM blocks WHERE "generator_public_key" = '{self.PublicKey}' ORDER BY "height" DESC LIMIT {val}""")
                return self.cursor.fetchall()
            except Exception as e:
                print(e)

        #else just grab last x for normal processing
        else:
            try:
                self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee",
                "height" FROM blocks WHERE "generator_public_key" = '{self.PublicKey}' and "height" > {h} ORDER BY "height" DESC LIMIT 50""")
                return self.cursor.fetchall()
            except Exception as e:
                print(e)    

    '''
    def voters(self):
        try:
            self.cursor.execute(f"""SELECT "address" FROM wallets WHERE "vote" = '{self.PublicKey}'""")

            voters=[]

            for addr in self.cursor.fetchall():
                self.cursor.execute(f"""SELECT "address","balance" FROM wallets WHERE "address" = '{addr[0]}'""")

                voters.append(self.cursor.fetchone())

            return voters
        except Exception as e:
            print(e)
     '''
