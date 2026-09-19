extends Node2D

const TILE := 16
const SOURCE_ID := 0

const MAP := [
	"##############################################",
	"#............................................#",
	"#............................................#",
	"#..##############............##############..#",
	"#..#++++++++++++#............#++++++++++++#..#",
	"#..#++==++++==++#............#++==++++==++#..#",
	"#..#++++++++++++#............#++++++++++++#..#",
	"#..####++++++####............####++++++####..#",
	"#.....#++++++#..................#++++++#.....#",
	"#.....#++++++#........PP........#++++++#.....#",
	"#.....#++++++####################++++++#.....#",
	"#.....#++++++++++++++++++++++++++++++++#.....#",
	"#.....#+++++++++++++~AA~+++++++++++++++#.....#",
	"#.....#++++++++++++++++++++++++++++++++#.....#",
	"#.....#++++++####################++++++#.....#",
	"#.....#++++++#..................#++++++#.....#",
	"#.....#++++++#..................#++++++#.....#",
	"#.....########..................########.....#",
	"#............................................#",
	"#...............ccc..........................#",
	"#............................................#",
	"#............................................#",
	"##############################################",
]

const GROUND_ATLAS := {
	".": Vector2i(0, 0),
	"+": Vector2i(1, 0),
	"~": Vector2i(2, 0),
	"=": Vector2i(1, 0),
	"c": Vector2i(0, 0),
	"A": Vector2i(2, 0),
	"P": Vector2i(0, 0),
}

const SOLID_ATLAS := {
	"#": Vector2i(3, 0),
	"=": Vector2i(4, 0),
	"c": Vector2i(5, 0),
	"A": Vector2i(6, 0),
	"P": Vector2i(7, 0),
}

const TILESET_TEXTURE: Texture2D = preload("res://assets/tileset.png")

@onready var ground: TileMapLayer = $Ground
@onready var solids: TileMapLayer = $Solids


func _ready() -> void:
	var tileset := _build_tileset()
	ground.tile_set = tileset
	solids.tile_set = tileset
	_paint()


func map_pixel_size() -> Vector2i:
	return Vector2i(MAP[0].length() * TILE, MAP.size() * TILE)


func _build_tileset() -> TileSet:
	var tileset := TileSet.new()
	tileset.tile_size = Vector2i(TILE, TILE)
	tileset.add_physics_layer()
	tileset.set_physics_layer_collision_layer(0, 1)
	tileset.set_physics_layer_collision_mask(0, 0)

	var source := TileSetAtlasSource.new()
	source.texture = TILESET_TEXTURE
	source.texture_region_size = Vector2i(TILE, TILE)
	for x in 8:
		source.create_tile(Vector2i(x, 0))
	tileset.add_source(source, SOURCE_ID)

	var full := PackedVector2Array([
		Vector2(-8, -8),
		Vector2(8, -8),
		Vector2(8, 8),
		Vector2(-8, 8),
	])
	for x in range(3, 8):
		var data: TileData = source.get_tile_data(Vector2i(x, 0), 0)
		data.add_collision_polygon(0)
		data.set_collision_polygon_points(0, 0, full)

	return tileset


func _paint() -> void:
	for y in MAP.size():
		var row: String = MAP[y]
		for x in row.length():
			var cell := row[x]
			var coords := Vector2i(x, y)
			if GROUND_ATLAS.has(cell):
				ground.set_cell(coords, SOURCE_ID, GROUND_ATLAS[cell])
			if SOLID_ATLAS.has(cell):
				solids.set_cell(coords, SOURCE_ID, SOLID_ATLAS[cell])
