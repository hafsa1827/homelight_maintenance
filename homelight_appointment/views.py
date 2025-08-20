from django.utils import timezone
from django.shortcuts import render
import uuid
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CalendarSerializer, CustomerRequestSerializer, InvoiceStatusUpdateSerializer,PaymentTransactionSerializer, InvoiceListSerializer,TechnicianStatusUpdateSerializer,IssueTechnicianSerializer,CustomerTroubleShootingListSerializer,TroubleShootingUpdatingSerializer,TroubleshootingCustomerRequestListSerializer,TechnicianTroubleShootingCreatingSerializer,TechnicianTroubleShootingSerializer, IssueTypeSerializer,RequestListSerializer,CustomerRequestListSerializer,TechnicianServiceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import calenders, invoice_history, invoices,technician_service_history, issue_type,customer_requests,technician_services,troubleshooting_history
from homelight_technician.models import technician_specialization
from homelight_users.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q


class CustomerRequestView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = CustomerRequestSerializer(
        data=request.data,
        context={'request': request}
    )
        if serializer.is_valid():
            saved_request = serializer.save()
            calenders.objects.create(
                user_id=saved_request.customer_id,
                date=saved_request.requested_date,  
                activity="Request Created"
            )
            return Response({'message': 'Request created and gallery saved'}, status=201)
        return Response(serializer.errors, status=400)

class IssueListView(APIView):
    def get(self, request):
        issues = issue_type.objects.all()
        serializer = IssueTypeSerializer(issues, many=True)
        return Response(serializer.data)
    
class IssueTechnicanListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        issues = technician_specialization.objects.filter(user=user_id)
        serializer = IssueTechnicianSerializer(issues, many=True)
        return Response(serializer.data)
    
class RequestInprogressAccept(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = technician_services.objects.filter(technician_id=user_id,request_id__status='In Progress',status='Accepted')
        serializer = RequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class RequestInprogressReject(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = technician_services.objects.filter(technician_id=user_id,request_id__status='Pending',status='Rejected')
        serializer = RequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class RequestListPending(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        specialization_issues = technician_specialization.objects.filter(user=user_id).values_list('issue', flat=True)
        matching_requests = customer_requests.objects.filter(
            status='Pending',
            issue_type__in=specialization_issues
        )
        serializer = CustomerRequestListSerializer(matching_requests, many=True, context={'request': request})
        return Response(serializer.data)

class RequestListInProgress(APIView):
    def get(self, request):
        galleries = customer_requests.objects.filter(status='In Progress')
        serializer = CustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class RequestListCompleted(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = technician_services.objects.filter(technician_id=user_id,request_id__status='Resolved')
        serializer = RequestListSerializer(galleries, many=True)
        return Response(serializer.data)

class RequestListDismissed(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = technician_services.objects.filter(technician_id=user_id,request_id__status='Dismissed')
        serializer = RequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class IssueRequestView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = customer_requests.objects.filter(customer_id=user_id,status='Pending')
        serializer = CustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class requestInprogressId_list(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = customer_requests.objects.filter(customer_id=user_id,status='In Progress')
        serializer = CustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class requestResolvedId_list(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = customer_requests.objects.filter(customer_id=user_id,status='Resolved')
        serializer = CustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class RequestDismissedId_list(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = customer_requests.objects.filter(customer_id=user_id,status='Dismissed')
        serializer = CustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
 
class IssueRequestId(APIView):
    def get(self, request):
        service_id = request.query_params.get('service_id')

        if not service_id:
            return Response({"error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = customer_requests.objects.filter(service_id=service_id)
        serializer = CustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class TechnicianServiceCreateView(APIView):
    def post(self, request):
        serializer = TechnicianServiceSerializer(data=request.data, context={'request': request}  )
        if serializer.is_valid():
            saved_request = serializer.save()

            calenders.objects.create(
                user_id=saved_request.technician_id,
                date=saved_request.created_at, 
                activity="Service Created"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TechnicianTroubleShootingCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        serializer = TechnicianTroubleShootingCreatingSerializer(
            data=request.data,
            context={'request': request}  
        )
        if serializer.is_valid():
            saved_request = serializer.save()

            calenders.objects.create(
                user_id=saved_request.request_id.technician_id,
                date=saved_request.resolved_at, 
                activity="Troubleshooting Created"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class troubleshootingList(APIView):
    def get(self, request):
        request_id = request.query_params.get('request_id', '').strip('"').strip('“”')
        if not request_id:
            return Response({"error": "Missing request_id"}, status=status.HTTP_400_BAD_REQUEST)

        services = technician_services.objects.filter(service_id=request_id)
        serializer = TechnicianTroubleShootingSerializer(services, many=True)
        return Response(serializer.data)
    
class TroubleshootingCustomerDismissedRequest_list(APIView):
    def get(self, request):
        service_id = request.query_params.get('service_id', '').strip('"').strip('“”') 
        if not service_id:
            return Response({"error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)
        galleries = technician_services.objects.filter(request_id=service_id,request_id__status='Dismissed')
        serializer = TroubleshootingCustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class TroubleshootingCustomerResolvedRequest_list(APIView):
    def get(self, request):
        service_id =  request.query_params.get('service_id', '').strip('"').strip('“”') 
        if not service_id:
            return Response({"error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)
        galleries = technician_services.objects.filter(request_id=service_id,request_id__status='Resolved')
        serializer = TroubleshootingCustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)

class TroubleshootingCustomerInprogressRequest_list(APIView):
    def get(self, request):
        service_id =  request.query_params.get('service_id', '').strip('"').strip('“”') 
        if not service_id:
            return Response({"error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)
        galleries = technician_services.objects.filter(request_id=service_id,request_id__status='In Progress')
        serializer = TroubleshootingCustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)

class TroubleshootingCustomerPendingRequest_list(APIView):
    def get(self, request):
        service_id = request.query_params.get('service_id', '').strip('"').strip('“”') 
        if not service_id:
            return Response({"error": "Missing service_id"}, status=status.HTTP_400_BAD_REQUEST)
        galleries = technician_services.objects.filter(request_id=service_id,request_id__status='Pending')
        serializer = TroubleshootingCustomerRequestListSerializer(galleries, many=True)
        return Response(serializer.data)
    
class UpdatingCustomerRequest_list(APIView):
    def get(self, request):
        request_id = request.query_params.get('request_id', '').strip('"').strip('“”')
        if not request_id:
            return Response({"error": "Missing request_id"}, status=status.HTTP_400_BAD_REQUEST)
        requests = technician_services.objects.filter(service_id=request_id)
        serializer = CustomerTroubleShootingListSerializer(requests, many=True)
        return Response(serializer.data)
    
class TroubleshootingUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, trouble_shoot_id):
        try:
            trouble = troubleshooting_history.objects.get(trouble_shoot_id=trouble_shoot_id)
        except troubleshooting_history.DoesNotExist:
            return Response({'error': 'Troubleshooting not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TroubleShootingUpdatingSerializer(
            trouble, data=request.data, partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            saved_request = serializer.save()
            calenders.objects.create(
                user_id=saved_request.request_id.technician_id,
                date=timezone.now(),  
                activity="TroubleShooting Updated"
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateTechnicianStatusAPIView(APIView):
    def post(self, request):
        service_id = request.data.get('service_id')
        new_status = request.data.get('new_status')
        price = float(request.data.get('technicianPrice', 0))
        userId = request.data.get('userId')
        rejectionReason= request.data.get('reason')
        if not service_id or not new_status:
            return Response({'error': 'Missing service_id or new_status'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = technician_services.objects.get(request_id=service_id,status="Select")
            requests= customer_requests.objects.get(service_id=service.request_id.service_id)
            if service.service_id:
                history, created = technician_service_history.objects.get_or_create(
                service_id=service.service_id,
                defaults={
                    'service_id':service.service_id,
                    'technician_id':service.technician_id,
                    'request_id':service.request_id,
                    'custom_price':service.custom_price,
                    'estimated_duration':service.estimated_duration,
                    'notes':service.notes,
                    'audio_url':service.audio_url,
                    'status': new_status,
                    'reason': rejectionReason
                }
            )
        except technician_services.DoesNotExist:
            return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TechnicianStatusUpdateSerializer(service, data={'status': new_status, 'reason':rejectionReason}, partial=True)
        
        if serializer.is_valid():
            saved_request = serializer.save()
            calenders.objects.create(
                user_id=CustomUser.objects.get(id=userId),
                date=timezone.now(),  
                activity="Service Booking Accepted"
            )
            
            if new_status == 'Accepted':
                new_invoices=invoices.objects.create(
                    request_id=service,
                    total_amount=price if price else 0,
                    status='OVERDUE',
                    invoice_date=now(),
                    user_id= CustomUser.objects.get(id=userId)
                )
                invoice_history.objects.create(
                    invoice_id=new_invoices.invoice_id,
                    request_id=new_invoices.request_id,
                    total_amount=new_invoices.total_amount,
                    status=new_invoices.status,
                    invoice_date=new_invoices.invoice_date,
                    user_id=new_invoices.user_id,
                    )
                calenders.objects.create(
                    user_id=CustomUser.objects.get(id=userId),
                    date=timezone.now(),  
                    activity="Service Booking Rejected"
                )
                
            elif new_status == "Rejected":
                requests.status="Pending"
                requests.save()
                calenders.objects.create(
                    user_id=CustomUser.objects.get(id=userId),
                    date=timezone.now(),  
                    activity="Service Booking Rejected"
                )
                

            return Response({'message': 'Technician status updated and invoice created'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnpaidInvoiceListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        role_id = request.query_params.get('role_id')
        TECHNICIAN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

        role_id_param = request.query_params.get("role_id", "").strip()
        try:
            role_id = uuid.UUID(role_id_param)
        except ValueError:
            return Response({"error": "Invalid role_id"}, status=400)

        if role_id == TECHNICIAN_ROLE_ID:
            invoice = invoices.objects.filter(status="UNPAID",request_id__technician_id=user_id)
        else:
            invoice = invoices.objects.filter(status="UNPAID",user_id=user_id)
            
        serializer = InvoiceListSerializer(invoice, many=True, context={'request': request})
        return Response(serializer.data)
class PaidInvoiceListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        role_id = request.query_params.get('role_id')
        TECHNICIAN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

        role_id_param = request.query_params.get("role_id", "").strip()
        try:
            role_id = uuid.UUID(role_id_param)
        except ValueError:
            return Response({"error": "Invalid role_id"}, status=400)

        if role_id == TECHNICIAN_ROLE_ID:
            invoice = invoices.objects.filter(status="PAID",request_id__technician_id=user_id)
        else:
            invoice = invoices.objects.filter(status="PAID",user_id=user_id)
            
        serializer = InvoiceListSerializer(invoice, many=True, context={'request': request})
        return Response(serializer.data)
class OverdueInvoiceListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id', '').strip()
        role_id = request.query_params.get('role_id', '').strip()
        TECHNICIAN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

        role_id_param = request.query_params.get("role_id", "").strip()
        try:
            role_id = uuid.UUID(role_id_param)
        except ValueError:
            return Response({"error": "Invalid role_id"}, status=400)

        if role_id == TECHNICIAN_ROLE_ID:
            invoice = invoices.objects.filter(status="OVERDUE", request_id__technician_id=user_id)
        else:
            invoice = invoices.objects.filter(status="OVERDUE", user_id=user_id)
            
        serializer = InvoiceListSerializer(invoice, many=True, context={'request': request})
        return Response(serializer.data)
class RefundedInvoiceListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        role_id_param = request.query_params.get("role_id", "").strip()

        TECHNICIAN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

        try:
            role_id = uuid.UUID(role_id_param)
        except ValueError:
            return Response({"error": "Invalid role_id"}, status=400)

        status_filter = Q(status="REFUND") | Q(status="REFUNDED")

        if role_id == TECHNICIAN_ROLE_ID:
            invoice = invoices.objects.filter(
                status_filter,
                request_id__technician_id=user_id
            )
        else:
            invoice = invoices.objects.filter(
                status_filter,
                user_id=user_id
            )

        serializer = InvoiceListSerializer(invoice, many=True, context={'request': request})
        return Response(serializer.data)
    
class WaitingVarificationInvoiceListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        role_id = request.query_params.get('role_id')
        TECHNICIAN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

        role_id_param = request.query_params.get("role_id", "").strip()
        try:
            role_id = uuid.UUID(role_id_param)
        except ValueError:
            return Response({"error": "Invalid role_id"}, status=400)

        if role_id == TECHNICIAN_ROLE_ID:
            invoice = invoices.objects.filter(status="WAITINGVARIFICATION",request_id__technician_id=user_id)
        else:
            invoice = invoices.objects.filter(status="WAITINGVARIFICATION",user_id=user_id)
            
        serializer = InvoiceListSerializer(invoice, many=True, context={'request': request})
        return Response(serializer.data)


class PaymentTransactionCreateView(APIView):
    def post(self, request):
        serializer = PaymentTransactionSerializer(data=request.data)
        if serializer.is_valid():
            saved_request = serializer.save()
            calenders.objects.create(
                user_id=saved_request.invoice_id.user_id,
                date=timezone.now(),  
                activity="Payment Created"
            )
            return Response({'message': 'Payment successful', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UpdateInvoiceStatusAPIView(APIView):
    def post(self, request):
        invoice_id = request.data.get('invoice_id')
        is_verified = request.data.get('varification')  # get the boolean flag
        print(is_verified)
        if not invoice_id:
            return Response({'error': 'Missing invoice_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = invoices.objects.get(pk=invoice_id)
        except invoices.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

        if invoice.status == "WAITINGVARIFICATION":
            new_status = "PAID" if is_verified else "UNPAID"
            serializer = InvoiceStatusUpdateSerializer(invoice, data={'status': new_status}, partial=True)
            if serializer.is_valid():
                saved_invoice = serializer.save()

                # Log only if it's verified and status is updated to PAID
                if new_status == "PAID":
                    calenders.objects.create(
                        user_id=saved_invoice.user_id,
                        date=timezone.now(),
                        activity="Invoice status updated to PAID"
                    )

                return Response({'message': f'Invoice status updated to {new_status}'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif invoice.status == "REFUNDED":
            invoice_history.objects.create(
                invoice_id=invoice.invoice_id,
                request_id=invoice.request_id,
                total_amount=invoice.total_amount,
                status=invoice.status,
                invoice_date=invoice.invoice_date,
                user_id=invoice.user_id,
            )
            invoice.delete()
            return Response({'message': 'Invoice status was REFUND, invoice archived and deleted'}, status=status.HTTP_200_OK)

        return Response({'message': f'No action taken. Invoice status is {invoice.status}'}, status=status.HTTP_200_OK)

class CalenderAPIView(APIView):
    def get(self, request):
        user = request.query_params.get('user_id')
        calendars = calenders.objects.filter(user_id=user)
        serializer = CalendarSerializer(calendars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)