from rest_framework import generics
from .models import Bank, Customer, Account, Deposit, Transaction, BankCustomer, Withdraw
from .serializers import BankSerializer,CustomerSerializer,AccountSerializer,DepositSerializer,TransactionSerializer,BankCustomerSerializer,WithdrawSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication




from django.db import transaction as db_transaction
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal  # Import Decimal for precise arithmetic



class BankListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 

    queryset = Bank.objects.all()
    serializer_class = BankSerializer


class CustomerListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class AccountListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 

    queryset = Account.objects.all()
    serializer_class = AccountSerializer



class BankCustomerListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 

    queryset = BankCustomer.objects.all()
    serializer_class = BankCustomerSerializer

from rest_framework.exceptions import ValidationError

class DepositListCreateView(generics.ListCreateAPIView):
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Deposit.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        account_id = serializer.validated_data['account'].id
        account = Account.objects.filter(user=self.request.user, id=account_id).first()
        if not account:
            raise ValidationError("Account not found or you don't have access to this account.")
        serializer.save(account=account)


class WithdrawListCreateView(generics.ListCreateAPIView):
    serializer_class = WithdrawSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Withdraw.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        account_id = serializer.validated_data['account'].id
        account = Account.objects.filter(user=self.request.user, id=account_id).first()
        if not account:
            raise ValidationError("Account not found or you don't have access to this account.")
        serializer.save(account=account)


class TransferAPIView(APIView):
    def post(self, request, *args, **kwargs):
        account_from_id = request.data.get('account_from')
        account_to_id = request.data.get('account_to')
        amount = request.data.get('amount')  # This is likely a float or string

        try:
            with db_transaction.atomic():
                # Validate accounts
                account_from = Account.objects.get(id=account_from_id)
                account_to = Account.objects.get(id=account_to_id)

                # Convert `amount` to Decimal
                amount = Decimal(amount)

                if account_from == account_to:
                    return Response({"error": "same acoount.."}, status=status.HTTP_400_BAD_REQUEST)

                if account_from.balance < amount:
                    return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

                # Update balances
                account_from.balance -= amount
                account_to.balance += amount
                account_from.save()
                account_to.save()

                # Create transaction record
                Transaction.objects.create(
                    account_from=account_from,
                    account_to=account_to,
                    amount=amount,
                    transaction_date=now(),
                )
                return Response({"message": "Transaction successful"}, status=status.HTTP_200_OK)

        except Account.DoesNotExist:
            return Response({"error": "One or both accounts do not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
