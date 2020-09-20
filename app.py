from flask import Flask, request, Response, jsonify
from database.db import initialize_db
from database.models import PVAParticipant, Result
import json

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/pva'
}

initialize_db(app)


#PVA users documents
@app.route('/pvausers')
def get_pvausers():
    pvausers = PVAParticipant.objects().to_json()
    return Response(pvausers, mimetype="application/json", status=200)

@app.route('/pvausers', methods=['POST'])
def add_pvauser():
    body = request.get_json()
    print(body)
    try:
        pvauser =  PVAParticipant(**body).save()
        id = pvauser.id
        return {"id": str(id)}, 200
    except:
        print("validator already saved or issue saving the new one")
        return {"result": "nok", "message":"validator already saved or issue saving the new one"}, 400

@app.route('/pvausers/<id>', methods=['PUT'])
def update_pvauser(id):
    body = request.get_json()
    PVAParticipant.objects.get(id=id).update(**body)
    return {"result": "ok"}, 200

@app.route('/pvausers/add/<pvaadd>', methods=['PUT'])
def update_pvauser_add(pvaadd):
    body = request.get_json()

    try:
        pvaobj = PVAParticipant.objects.get(validatoraddress=pvaadd)
    except:
        print("validator non existent")
        return {"result": "nok", "message":"validator non existent"}, 400
    print(body)
    #PVAParticipant.objects.get(id=pvaobj).update(**body)
    return {"result": "ok"}, 200


@app.route('/pvausers/<id>', methods=['DELETE'])
def delete_pvauser(id):
    pvauser = PVAParticipant.objects.get(id=id).delete()
    return {"result": "ok"}, 200

@app.route('/pvausers/<id>')
def get_pvauser(id):
    pvauser = PVAParticipant.objects.get(id=id).to_json()
    return Response(pvauser, mimetype="application/json", status=200)


#results
@app.route('/pvausers/results')
def get_results():
    result = Result.objects().to_json()
    return Response(result, mimetype="application/json", status=200)

@app.route('/pvausers/<pvaid>/results')
def get_pvauser_results(pvaid):
    result = Result.objects(pvauser=pvaid).to_json()
    return Response(result, mimetype="application/json", status=200)

@app.route('/pvausers/<pvaid>/results', methods=['POST'])
def add_pvauser_result(pvaid):
    body = request.get_json()
    print(body)
    pvauserresult =  Result(**body).save()
    id = pvauserresult.id
    return {"id": str(id)}, 200

@app.route('/pvausers/add/<pvaadd>/results', methods=['POST'])
def add_pvauser_result_add(pvaadd):
    body = request.get_json()
    print(body)
    body.pvauser = PVAParticipant.objects.get(validatoraddress=pvaadd)
    print(body)
    #pvauserresult =  Result(**body).save()
    id = pvauserresult.id
    return {"id": str(id)}, 200

@app.route('/pvausers/<pvaid>/results/<challengename>')
def get_pvauser_result(pvaid, challengename):
    result = Result.objects(pvauser=pvaid, gamename=challengename).to_json()
    return Response(result, mimetype="application/json", status=200)

@app.route('/pvausers/<pvaid>/results/<challengename>', methods=['PUT'])
def update_pvauser_result(pvaid, challengename):
    body = request.get_json()
    print(body)
    Result.objects(pvauser=pvaid, gamename=challengename).update(**body)
    return {"result": "ok"}, 200

@app.route('/pvausers/add/<pvaadd>/results/<challengename>')
def get_pvauser_result_via_add(pvaadd, challengename):
    pvaid = PVAParticipant.objects.get(validatoraddress=pvaadd)
    result = Result.objects(pvauser=pvaid, gamename=challengename).to_json()
    print (result)
    return Response(result, mimetype="application/json", status=200)

@app.route('/pvausers/add/<pvaadd>/results/<challengename>', methods=['PUT'])
def update_pvauser_result_via_add(pvaadd, challengename):
    body = request.get_json()
    print(body)
    try:
        pvaobj = PVAParticipant.objects.get(validatoraddress=pvaadd)
    except:
        print("validator non existent")
        return {"result": "nok", "message":"validator non existent"}, 400    
    try:
        Result.objects(pvauser=pvaobj.id, gamename=challengename).update(**body)
        return f"{{\"result\": \"ok\", \"message\":\"{challengename} updated\"}}", 200
    except:
        return {"result": "nok", "message":"update failed"}, 400

@app.route('/pvausers/add/<pvaadd>/results/<challengename>', methods=['POST'])
def create_pvauser_result_via_add(pvaadd, challengename):
    body = request.get_json()
    try:
        pvaobj = PVAParticipant.objects.get(validatoraddress=pvaadd)
    except:
        print("validator non existent")
        return {"result": "nok", "message":"validator non existent"}, 400

    print(pvaobj.id)
    content={
        "pvauser": pvaobj.id,
        "gamename": challengename,
        "gameresult": 1
    }
    try:
        Result(**content).save()
        return {"result": "ok", "message":"game created"}, 200
    except:
        return {"result": "nok", "message":"result not created, most likely already created"}, 400

app.run(host= '127.0.0.1', debug= True)
