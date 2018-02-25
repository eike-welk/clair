module Main exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as Decode


main =
    Html.program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL


type alias SearchTask =
    { id : String
    , name : String

    --, search_words : String
    }


type alias Model =
    List SearchTask


init : ( Model, Cmd Msg )
init =
    ( [ SearchTask "1" "foo", SearchTask "2" "bar" ]
    , Cmd.none
    )



-- UPDATE


type Msg
    = MorePlease



--    | NewGif (Result Http.Error String)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        MorePlease ->
            ( model, Cmd.none )



{--
        NewGif (Ok newUrl) ->
            ( { model | gifUrl = newUrl, errorMsg = "" }, Cmd.none )

        NewGif (Err _) ->
            ( { model | errorMsg = "A network error occurred" }, Cmd.none )
            --}
-- VIEW


view : Model -> Html Msg
view model =
    div []
        [ h2 [] [ text "Search Tasks" ]
        , br [] []
        , table []
            [ thead []
                [ tr [] [ th [] [ text "name" ] ]
                ]
            , tbody []
                (List.map viewSearchTask model)
            ]
        , button [ onClick MorePlease ] [ text "More Please!" ]
        ]


viewSearchTask : SearchTask -> Html Msg
viewSearchTask task =
    tr [] [ td [] [ text task.name ] ]



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- HTTP
{--
getRandomGif : String -> Cmd Msg
getRandomGif topic =
    let
        url =
            "https://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=" ++ topic
    in
        Http.send NewGif (Http.get url decodeGifUrl)


decodeGifUrl : Decode.Decoder String
decodeGifUrl =
    Decode.at [ "data", "image_url" ] Decode.string
    --}
