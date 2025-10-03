from whoop_pipeline.models import Sleep, Recovery, Workout, Cycle

def test():
    model_classes = {'cycle': Cycle,
                    'activity/sleep': Sleep, 
                    'recovery': Recovery,
                    'activity/workout': Workout
                    }
    return model_classes


if __name__ == '__main__':
    models = test()

    table_info = {}

    for key, model in models.items():
        columns = []
        for col in model.__table__.columns:
            columns.append({
                'name': col.name,
                'type': str(col.type),
                'nullable': col.nullable,
                'primary_key': col.primary_key
            })
        table_info[key] = columns

    print(table_info)