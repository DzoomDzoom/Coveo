from game_message import *
from actions import *
import random

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self.isAtShield = False
        self.isAtTurret = False
        self.isAtRadar = False
        self.isAtHelm = False
        self.count = 2

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
        shipId = other_ships_ids[0]
        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]

        for crewmate in idle_crewmates:
            visitable_shields = crewmate.distanceFromStations.shields 
            visible_turrets = crewmate.distanceFromStations.turrets 
            visible_helms = crewmate.distanceFromStations.helms
            shield_to_move_to = random.choice(visitable_shields)
            turret_to_move_to = random.choice(visible_turrets)
            helm_to_move_to = random.choice(visible_helms)
            if(self.isAtShield == False):
                actions.append(CrewMoveAction(crewmate.id, shield_to_move_to.stationPosition))
                self.isAtShield = True
                continue
            if(self.count != 0):
                actions.append(CrewMoveAction(crewmate.id, turret_to_move_to.stationPosition))
                self.count -= 1
                continue
            if(self.isAtHelm ==False):
                actions.append(CrewMoveAction(crewmate.id, helm_to_move_to.stationPosition))
                self.isAtHelm = True
                continue
            
        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            possible_actions = [
                # Charge the turret.
                TurretChargeAction(turret_station.id),
                # Aim the turret itself.
                TurretLookAtAction(turret_station.id, 
                                   Vector(game_message.shipsPositions.get(shipId).x, game_message.shipsPositions.get(shipId).y))
                ,
                # Shoot!
                TurretShootAction(turret_station.id)
            ]

            actions.append(random.choice(possible_actions))

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        if operatedHelmStation:
            actions.append(ShipLookAtAction(game_message.shipsPositions.get(shipId)))

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

        # You can clearly do better than the random actions above! Have fun!
        return actions
