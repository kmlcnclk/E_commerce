from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    handlers = [
        {'errorName': 'ValidationError',
         'status_code': '400'},
        {'errorName': 'Http404',
         'status_code': '404'},
        {'errorName': 'PermissionDenied',
         'status_code': '403'},
        {'errorName': 'NotAuthenticated',
         'status_code': '401'},
        {'errorName': 'BadRequest',
         'status_code': '400'},
        {'errorName': 'MethodNotAllowed',
         'status_code': '405'},
        {'errorName': 'ImportError',
         'status_code': '500'},
        {'errorName': 'IntegrityError',
         'status_code': '500'},
        {'errorName': 'NameError',
         'status_code': '500'},
        {'errorName': 'AttributeError',
         'status_code': '500'},
        {'errorName': 'TokenError',
         'status_code': '401'},
        {'errorName': 'DoesNotExist',
         'status_code': '404'},
    ]

    response = exception_handler(exc, context)

    if response is not None:
        # import pdb
        # pdb.set_trace()

        if 'AuthUserAPIView' in str(context['view']) and exc.status_code == 401:
            response.status_code = 200
            response.data = {'is_logged_in': False}

            return response

        response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__

    if str(exc).split('Detail: ')[0] != '':
        exc_message = str(exc).split('Detail: ')
    else:
        exc_message = None
    # print(context)
    # print(exc)

    for handler in handlers:
        if exception_class in handler.get('errorName'):
            # print(handlers[exception_class](exc, context, response))
            # print(handler.get('errorName'))
            # print('1')

            return Response({
                'error': {
                    'name': handler.get('errorName'),
                    'message': exc_message or handler.get('errorName'),
                    'status_code':  handler.get('status_code'),
                }
            },  status=handler.get('status_code'))
        # return handlers[exception_class](exc, context, response)
    return response


# def _handle_authentication_error(exc, context, response):
#     response.data = {
#         'error': 'Please login to proced',
#         'status_code': response.status_code

#     }

#     return response


# def _handle_generic_error(exc, context, response):

#     return response


# def _handle_bad_request_error(exc, context, response):
#     # print(exc)
#     response.data = {
#         'error': {
#             'name': 'BadRequest',
#             'message': exc,
#             'status_code': '400',
#         }
#     }
#     return Response(response)
