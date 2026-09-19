extends Node2D

const TILE := 16
const InteractionCircleScene := preload("res://scenes/interaction_circle.tscn")


func _ready() -> void:
	var circle := InteractionCircleScene.instantiate()
	circle.duration = 3.0
	circle.should_restart = false
	circle.radius = TILE * 1.5 / 2.0
	circle.position = $Player.position + Vector2(TILE * 3, 0)
	circle.on_completed = GameState.add.bind(5)
	add_child(circle)
