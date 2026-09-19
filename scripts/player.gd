extends CharacterBody2D

@export var speed: float = 64.0

@onready var sprite: Sprite2D = $Sprite2D

var _walk_time: float = 0.0


func _physics_process(delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * speed

	if direction.x != 0.0:
		sprite.flip_h = direction.x < 0.0

	if direction != Vector2.ZERO:
		_walk_time += delta * 8.0
		sprite.frame = int(_walk_time) % 2
	else:
		_walk_time = 0.0
		sprite.frame = 0

	move_and_slide()
