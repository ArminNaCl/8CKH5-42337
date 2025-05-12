from django.test import TestCase
from datetime import datetime
from .models import Table, Reserve
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from .services import ReserveService

class TableReservationTestCase(TestCase):
    
    def setUp(self):
        Table.objects.create(
            capacity=4, 
            price=100, 
            id=1
        )
        Table.objects.create(
            capacity=6, 
            price=150, 
            id=2
        )
        Table.objects.create(
            capacity=2, 
            price=80, 
            id=3
        )
        User.objects.create(
            id=1,
            username="user1"
        )
        
        Reserve.objects.create(
            table_id=1,
            user_id=1,
            number_of_people=4,
            number_of_seats=4,
            date=datetime(2025, 5, 15),
            from_time=datetime(2025, 5, 15, 18, 0),
            to_time=datetime(2025, 5, 15, 20, 0),
            amount=400,
            status=Reserve.Status.BOOKED
        )

    def test_return_table_for_odd_number_of_people(self):
        user_id=1
        number_of_people = 3
        date = datetime(2025, 5, 15)
        from_time = datetime(2025, 5, 15, 19, 0)
        to_time = datetime(2025, 5, 15, 21, 0)

        reserve = ReserveService().create_reserve(user_id,number_of_people, date, from_time, to_time)

        # Validate that the table returned has enough capacity and is the cheapest
        self.assertEqual(reserve.table.id, 2)
        self.assertEqual(reserve.amount, 750.0)

    def test_return_table_for_even_number_of_people(self):
        user_id=1
        number_of_people = 4
        date = datetime(2025, 5, 15)
        from_time = datetime(2025, 5, 15, 19, 0)
        to_time = datetime(2025, 5, 15, 21, 0)

        reserve = ReserveService().create_reserve(user_id,number_of_people, date, from_time, to_time)        
        
        self.assertEqual(reserve.table.id, 2)
        self.assertEqual(reserve.amount, 600.0)

    def test_no_available_table(self):
        user_id=1
        number_of_people = 5
        date = datetime(2025, 5, 15)
        from_time = datetime(2025, 5, 15, 19, 0)
        to_time = datetime(2025, 5, 15, 21, 0)
        Reserve.objects.create(
            table_id=2,
            user_id=1,
            number_of_people=4,
            number_of_seats=4,
            date=datetime(2025, 5, 15),
            from_time=datetime(2025, 5, 15, 18, 0),
            to_time=datetime(2025, 5, 15, 20, 0),
            amount=400,
            status=Reserve.Status.BOOKED
        )

        with self.assertRaises(ValidationError) as context:
            ReserveService().create_reserve(user_id,number_of_people, date, from_time, to_time)
            self.assertEqual(context.exception.message, "No Table is Available Right Now")
            

