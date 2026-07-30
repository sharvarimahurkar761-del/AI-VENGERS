from app.models.predict import predict_risk


def test_prediction_range():

    sample = [
        0.55,
        3,
        0.72,
        0.60,
        2,
        14,
        3
    ]

    score = predict_risk(sample)

    assert 0 <= score <= 1