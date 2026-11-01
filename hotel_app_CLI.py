class Hotel:
    def __init__ (self , single_room , dubble_room , resturant , pool):
        self.single_room = single_room
        self.dubble_room = dubble_room
        self.resturant = resturant
        self.pool = pool
        self.names_in_single = []
        self.names_in_dubble = []
    @property
    def show_details (self):
        return (
            f'\nTHIS HOTEL HAS://\n\n\t1) {self.single_room.get_available_count} Single Rooms\n\t2)'
            f' {self.dubble_room.get_available_count} Dubble Rooms'
            f'\n\t3) {self.resturant} Resturants\n\t4) {self.pool} Pools\n'
        )

class Rooms:
    def __init__ (self , day , price , num_room ):
        self.day = day
        self.price = price
        self.num_room = num_room
        pass


class SingleRoom(Rooms):
    def __init__ (self , day=0 , price=500 , num_room=0):
        super().__init__ (day , price , num_room)
        self.__num_of_available_single_rooms = 5
        self.num_room = 100
        self.price = price

    @property
    def is_available (self):
        return self.__num_of_available_single_rooms > 0
    @property
    def get_available_count(self):
        return self.__num_of_available_single_rooms
    @property
    def book_room (self):
        if self.is_available:
            self.__num_of_available_single_rooms -= 1
            print('\n*  *  *  Book Successful  *  *  *\n')
            return True
        else:
            print('\n  *  *  Booking Failed. No Rooms Available.  *  *\n')
            return False
    @property
    def single (self , price=500):
        self.price = price
        self.num_room += 1
        return (
            f'Single Room Number {self.num_room} is Currently Available, '
            f'And The Price is {self.price * self.day} For {self.day} Days'
        )       
    
    @property
    def check_out_single(self):
        self.__num_of_available_single_rooms += 1
        self.num_room -= 1
        return ''

            


class DubbleRoom(Rooms):
    def __init__ (self , day=0 , price=700 , num_room=0):
        super().__init__ (day  , price, num_room)
        self.__num_of_available_dubble_room = 5
        self.num_room = 105
        self.price = price
    @property
    def is_available(self):
        return self.__num_of_available_dubble_room > 0
    @property
    def get_available_count(self):
        return self.__num_of_available_dubble_room   
    @property
    def book_room(self):
        if self.is_available:
            self.__num_of_available_dubble_room -= 1    
            print('\n*  *  *  Book Successful  *  *  *\n')
            return True
        else:
            print('\n  *  *  Booking Failed. No Rooms Available.  *  *\n')
            return False
    @property    
    def dubble (self , price=700):
        self.num_room += 1
        self.price = price
        return (
            f'Dubble Room Number {self.num_room} is Currently Available, '
            f'And The Price is {self.price * self.day} For {self.day} Days'
        )
    
    @property
    def check_out_dubble (self):
        self.__num_of_available_dubble_room += 1
        self.num_room -= 1
        return ''



class Booking:
    def __init__ (self , client_name='' , num_of_days=0 , room_obj=''):
        self.client_name = client_name
        self.num_of_days = num_of_days
        self.room_obj = room_obj
    @property
    def book (self):
        return f'Hello Mr/Miss {self.client_name} You Have Booked {self.num_of_days} Days\n'

        


single_room = SingleRoom()
dubble_room = DubbleRoom()
details = Hotel(single_room,dubble_room,2,5)

while True:
    print('--------------------')
    print('1 : For Show Details From Hotel')      
    print(f'\n2 : For Booking Single Room\n'
          f'    The Price Per Night For One Room Is {single_room.price}'
          )
    print(f'\n3 : For Booking Dubble Room\n'
          f'    The Price Per Night For One Room Is {dubble_room.price}'
          )
    print('\n4 : For Show Bookers :')
    print('\n5 : For Check Out :')
    print('\n6 : For Exit')
    print('--------------------')

    choice = input("Enter Your Choice (1 : 6) : ")
    if choice == '1':                                            #  Choice [ 1 ]    [ Show Details ]
        print(details.show_details)


    elif choice == '2':                                          #  Choice [ 2 ]    [ Single Rooms ]
        print("Enter Your Name")
        name = input("Enter Your Name: ")
        print("Enter The Number Of Days You Would Like To Book: ")
        try:
            days = int(input("Enter The Number Of Days: "))
        except ValueError as er:
            print('Please Enter Positive Number')
            continue
        single_room.day = days

        if single_room.book_room:
            user_book = Booking(name , days , single_room)
            details.names_in_single.append(name)
            print(single_room.single)
            print(user_book.book)
            

    elif choice == '3':                                          #  Choice [ 3 ]    [ Dubble Rooms ]
        print("Enter Your Name")
        name = input("Enter Your Name: ")
        print("Enter The Number Of Days You Would Like To Book: ")
        try:
            days = int(input("Enter The Number Of Days: "))
        except ValueError as er:
            print('Please Enter Positive Number')
            continue
        dubble_room.day = days

        if dubble_room.book_room:
            user_book = Booking(name , days , dubble_room)
            details.names_in_dubble.append(name)
            print(dubble_room.dubble)
            print(user_book.book)


    elif choice == '4':                                          #  Choice [ 4 ]    [ Show Bookers ]
        show = Booking()
        all_bookers = details.names_in_single + details.names_in_dubble
        print(f"\nAll Bookers: {all_bookers}\n")

    elif choice == '5':                                          #  Choice [ 5 ]     [ Check Out ]
        while True:
            print("1 : For Check Out In Single Room\n2 : For Check Out In Dubble Room")
            chioce = input("Enter Your Choice: ")
            if chioce == '1':
                name_check_out = input("Enter Your Name To Check Out: ")

                if name_check_out in details.names_in_single:
                    details.names_in_single.remove(name_check_out)
                    print(f'Hello Mr/Miss {name_check_out} Your Check Out Successful{single_room.check_out_single}')
                    break

                else:
                    print('Please Enter The Name Exactly As It Appears In The Booking')
                    break

            elif chioce == '2':
                name_check_out = input("Enter Your Name To Check Out: ")

                if name_check_out in details.names_in_dubble:
                    details.names_in_dubble.remove(name_check_out)
                    print(f'Hello Mr/Miss {name_check_out} Your Check Out Successful{dubble_room.check_out_dubble}')
                    break

                else:
                    print('Please Enter The Name Exactly As It Appears In The Booking')
                    break


    elif choice == '6':
        print('Exiting...')
        break

    else:
        print(" * * * Enter Number (1 : 5) * * * ")



