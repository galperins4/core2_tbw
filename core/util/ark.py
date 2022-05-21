import psycopg2

class ArkDB:
    def __init__(self, db, dbh, u, pw, pk):
        self.db=db
        self.host=dbh
        self.user=u
        self.password=pw
        self.PublicKey=pk
    
    
    def open_connection(self):
        self.connection = psycopg2.connect(
            dbname = self.db,
            user = self.user,
            password= self.password,
            host=self.host,
            port='5432')
            
        self.cursor=self.connection.cursor()
    
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
    
    
    def blocks(self, i='no', val=1, h=None):
        
        #if i is yes, first run grab every block forged for history
        if i == 'yes':
            try:
                self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee", "height",
                "burned_fee" FROM blocks WHERE "generator_public_key" = '{self.PublicKey}' ORDER BY "height" DESC""")
                return self.cursor.fetchall()
            except Exception as e:
                print(e)

        #else just grab last x for normal processing
        else:
            try:
                self.cursor.execute(f"""SELECT "id","timestamp","reward","total_fee", "height",
                "burned_fee" FROM blocks WHERE "generator_public_key" = '{self.PublicKey}' and "height" > {h} ORDER BY "height" DESC LIMIT 250""")
                return self.cursor.fetchall()
            except Exception as e:
                print(e)
