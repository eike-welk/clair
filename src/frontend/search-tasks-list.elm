module Main exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as Decode
import Debug exposing (log)


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
    , queryString : String

    --, search_words : String
    }


type alias Model =
    { tasks : List SearchTask
    , error : String
    }


init : ( Model, Cmd Msg )
init =
    ( Model [ SearchTask "1" "foo", SearchTask "2" "bar" ] ""
    , Cmd.none
    )



-- UPDATE


type Msg
    = MorePlease
    | NewTasks (Result Http.Error (List SearchTask))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        MorePlease ->
            ( model, getTaskList )

        NewTasks (Ok newTasks) ->
            ( { model | tasks = newTasks }, Cmd.none )

        NewTasks (Err err) ->
            ( { model | error = (toString err) }, Cmd.none )



-- VIEW


view : Model -> Html Msg
view model =
    div []
        [ h2 [] [ text "Search Tasks" ]
        , br [] []
        , table []
            [ thead []
                [ tr []
                    [ th [] [ text "ID" ]
                    , th [] [ text "Query String" ]
                    ]
                ]
            , tbody []
                (List.map viewSearchTask model.tasks)
            ]
        , button [ onClick MorePlease ] [ text "More Please!" ]
        ]


viewSearchTask : SearchTask -> Html Msg
viewSearchTask task =
    tr []
        [ td [] [ text task.id ]
        , td [] [ text task.queryString ]
        ]



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- HTTP


getTaskList : Cmd Msg
getTaskList =
    let
        url =
            "http://localhost:8000/collect/api/search_tasks/"
    in
        Http.send NewTasks (Http.get url decodeGifUrl)


decodeGifUrl : Decode.Decoder (List SearchTask)
decodeGifUrl =
    Decode.at [ "results" ]
        (Decode.list
            (Decode.map2 makeSearchTask
                (Decode.at [ "id" ] Decode.int)
                (Decode.at [ "query_string" ] Decode.string)
            )
        )


makeSearchTask : Int -> String -> SearchTask
makeSearchTask id queryString =
    SearchTask (log "id" (toString id)) (log "queryString" queryString)
